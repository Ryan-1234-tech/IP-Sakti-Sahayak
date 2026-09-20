"""
routers/upload.py — POST /api/upload
"""
import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.models.db import UploadedDocument
from app.models.schemas import UploadResponse
from app.services.document_intel import extract_text_from_pdf

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


@router.post("/upload", response_model=UploadResponse, summary="Upload a PDF document")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload a PDF document for text extraction and later analysis.

    Returns a `document_id` to use with `POST /api/document/analyze`.
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES and not (
        file.filename and file.filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported.",
        )

    # Read and size-check
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.max_upload_size_bytes // (1024*1024)} MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Extract text
    try:
        extracted_text, page_count = extract_text_from_pdf(file_bytes)
    except Exception as e:
        logger.exception(f"PDF extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text from this PDF. The file may be corrupted.",
        )

    # Persist to DB
    doc_id = str(uuid.uuid4())
    doc = UploadedDocument(
        id=doc_id,
        filename=file.filename or "unnamed.pdf",
        file_size=len(file_bytes),
        extracted_text=extracted_text,
    )
    db.add(doc)

    return UploadResponse(
        document_id=doc_id,
        filename=file.filename or "unnamed.pdf",
        file_size=len(file_bytes),
        extracted_text_preview=extracted_text[:500],
        page_count=page_count,
    )
