"""
services/document_intel.py — PDF document extraction and AI-powered analysis.

Workflow (from architecture §6):
  Upload PDF
    → PyMuPDF text extraction
    → if text is near-empty, OCR via Tesseract
    → classify doc type (single LLM call)
    → extract key fields + deadline (LLM call → structured JSON)
    → return DocumentSummary
"""
from __future__ import annotations

import io
import json
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

from app.models.schemas import DocumentSummary

logger = logging.getLogger(__name__)


# ============================================================
# Text extraction
# ============================================================

def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from a PDF byte string using PyMuPDF.
    Falls back to pytesseract OCR for pages where text extraction is empty.

    Returns:
        (extracted_text, page_count)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF (fitz) is not installed.")
        raise

    text_parts: list[str] = []
    page_count = 0

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)

    for page_num, page in enumerate(doc):
        page_text = page.get_text("text").strip()

        if not page_text:
            # Try OCR on this page
            page_text = _ocr_page(page)
            if page_text:
                logger.debug(f"Page {page_num + 1}: used OCR ({len(page_text)} chars)")

        if page_text:
            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")

    doc.close()
    full_text = "\n\n".join(text_parts)
    return full_text, page_count


def _ocr_page(page) -> str:
    """Run pytesseract OCR on a single PyMuPDF page object."""
    try:
        import pytesseract
        from PIL import Image

        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang="eng+hin")
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""


def is_text_sufficient(text: str, min_chars: int = 100) -> bool:
    """Return True if the extracted text has enough content for analysis."""
    return len(text.strip()) >= min_chars


# ============================================================
# LLM-based document classification and field extraction
# ============================================================

_CLASSIFY_PROMPT = """You are analyzing an Indian IP or AYUSH regulatory document.

Classify this document and extract key information. Respond with valid JSON only:

{{
  "doc_type": "<one of: patent_application, trademark_application, examination_notice, certificate, office_action, faq, guideline, circular, form, other>",
  "summary": "<2-3 sentence plain-English summary of what this document is and what it requires>",
  "deadline_date": "<ISO date YYYY-MM-DD if a deadline is mentioned, otherwise null>",
  "key_requirements": ["<requirement 1>", "<requirement 2>", ...]
}}

Document text (first 3000 characters):
{text_excerpt}
"""


def classify_and_extract(text: str) -> DocumentSummary:
    """
    Use the LLM to classify a document type and extract structured fields.

    Args:
        text: Full extracted text from the PDF.

    Returns:
        A DocumentSummary with doc_type, summary, deadline_date, key_requirements.
    """
    from app.services.llm import complete_json

    excerpt = text[:3000].strip()
    if not excerpt:
        return DocumentSummary(
            doc_type="other",
            summary="Could not extract readable text from this document.",
            deadline_date=None,
            key_requirements=[],
        )

    prompt = _CLASSIFY_PROMPT.format(text_excerpt=excerpt)

    try:
        raw = complete_json(prompt, max_tokens=512)
        data = json.loads(raw)
        return DocumentSummary(
            doc_type=data.get("doc_type", "other"),
            summary=data.get("summary", ""),
            deadline_date=data.get("deadline_date"),
            key_requirements=data.get("key_requirements", []),
        )
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse classification JSON: {e}\nRaw: {raw!r}")
        # Attempt simple fallback extraction
        return DocumentSummary(
            doc_type="other",
            summary=_simple_summary(text),
            deadline_date=_extract_date_heuristic(text),
            key_requirements=[],
        )


# ============================================================
# Heuristic fallbacks
# ============================================================

def _simple_summary(text: str) -> str:
    """Return the first meaningful paragraph as a fallback summary."""
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 40]
    return " ".join(lines[:3])[:500] if lines else "Document summary unavailable."


_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}|"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)


def _extract_date_heuristic(text: str) -> Optional[str]:
    """Return the first date-like string found in the text, or None."""
    match = _DATE_PATTERN.search(text)
    return match.group(0) if match else None
