"""
routers/document.py — POST /api/document/analyze
"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db import UploadedDocument
from app.models.schemas import DeadlineInfo, DocumentAnalyzeRequest, DocumentAnalyzeResponse
from app.services.document_intel import classify_and_extract
from app.services.rag import answer_query

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/document/analyze",
    response_model=DocumentAnalyzeResponse,
    summary="Analyze an uploaded document",
)
async def analyze_document(
    request: DocumentAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
) -> DocumentAnalyzeResponse:
    """
    Classify and extract key information from a previously uploaded document.

    Optionally accepts a question — if provided, runs the extracted text through
    the RAG pipeline as additional context.
    """
    # Fetch uploaded document
    doc: UploadedDocument | None = await db.get(UploadedDocument, request.document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{request.document_id}' not found. Upload it first via POST /api/upload.",
        )

    extracted_text = doc.extracted_text or ""

    # If we've already classified this document, return cached summary
    if doc.summary_json:
        try:
            cached = json.loads(doc.summary_json)
            summary_obj = _build_summary(cached)
        except (json.JSONDecodeError, TypeError):
            summary_obj = None
    else:
        summary_obj = None

    if summary_obj is None:
        # Classify + extract via LLM (two LLM calls max as per architecture §6)
        summary_obj = classify_and_extract(extracted_text)
        doc.summary_json = json.dumps(summary_obj.model_dump())

    # Build deadline info (Feature 6)
    deadline = None
    if summary_obj.deadline_date:
        try:
            from datetime import datetime
            d_date = datetime.strptime(summary_obj.deadline_date[:10], "%Y-%m-%d")
            now = datetime.now()
            days_left = (d_date - now).days
            days_str = f"{days_left} days remaining" if days_left >= 0 else "Deadline Passed"
        except Exception:
            days_str = "Extracted deadline"

        deadline = DeadlineInfo(
            deadline_date=summary_obj.deadline_date,
            description=f"Response deadline extracted from document ({days_str})",
        )
    else:
        deadline = DeadlineInfo(
            deadline_date=None,
            description="Could not identify a deadline in the uploaded document."
        )


    # If a question was asked, run RAG with document as extra context
    rag_response = None
    if request.question:
        try:
            rag_response = await answer_query(
                query=request.question,
                language=request.language,
                extra_context=extracted_text,
            )
        except Exception as e:
            logger.warning(f"RAG call failed for document question: {e}")

    return DocumentAnalyzeResponse(
        document_id=request.document_id,
        summary=summary_obj,
        deadline=deadline,
        requirements=summary_obj.key_requirements,
        sources=rag_response.sources if rag_response else [],
        confidence=rag_response.confidence if rag_response else "MEDIUM",
        confidence_score=rag_response.confidence_score if rag_response else 0.0,
        answer=rag_response.answer if rag_response else None,
    )


def _build_summary(data: dict):
    from app.models.schemas import DocumentSummary
    return DocumentSummary(
        doc_type=data.get("doc_type", "other"),
        summary=data.get("summary", ""),
        deadline_date=data.get("deadline_date"),
        key_requirements=data.get("key_requirements", []),
    )
