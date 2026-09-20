#!/usr/bin/env python3
"""
scripts/ingest.py — Offline knowledge-base ingestion script.

Preserves full metadata provenance (Step 3 & 4):
    source_id, title, authority, source_type, jurisdiction, section, article,
    rule, page_number, document_version, effective_date, source_url, chunk_id
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure the backend root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, init_db
from app.models.db import Source
from app.services.document_intel import extract_text_from_pdf
from app.services.vector_store import add_documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest")
settings = get_settings()


# ---------------------------------------------------------------------------
# Section / Provision heuristics
# ---------------------------------------------------------------------------

def detect_section_or_rule(chunk_text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Detect section, rule, or article from chunk text."""
    sec_match = re.search(r"\b(Section\s+\d+[A-Za-z]?(?:\(\d+\))*(?:\([a-z]\))*)\b", chunk_text, re.IGNORECASE)
    section = sec_match.group(1) if sec_match else None

    rule_match = re.search(r"\b(Rule\s+\d+[A-Za-z]?(?:\(\d+\))*)\b", chunk_text, re.IGNORECASE)
    rule = rule_match.group(1) if rule_match else None

    art_match = re.search(r"\b(Article\s+\d+[A-Za-z]?(?:\(\d+\))*)\b", chunk_text, re.IGNORECASE)
    article = art_match.group(1) if art_match else None

    return section, rule, article


# ---------------------------------------------------------------------------
# Chunking with Page Tracking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 90,
) -> List[str]:
    """Split text into overlapping word chunks."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------------------------
# Metadata extraction from filename
# ---------------------------------------------------------------------------

def metadata_from_filename(filepath: Path) -> Dict[str, Any]:
    stem = filepath.stem.lower()
    parts = stem.split("_")

    authority_map = {
        "ipindia": ("IP India", "INDIA"),
        "ip": ("IP India", "INDIA"),
        "ayush": ("Ministry of AYUSH", "INDIA"),
        "nba": ("National Biodiversity Authority", "INDIA"),
        "biodiversity": ("National Biodiversity Authority", "INDIA"),
        "wipo": ("WIPO", "INTERNATIONAL"),
        "pct": ("WIPO", "INTERNATIONAL"),
        "trips": ("WTO / WIPO", "INTERNATIONAL"),
        "uspto": ("USPTO", "INTERNATIONAL"),
        "epo": ("EPO", "INTERNATIONAL"),
        "tkdl": ("TKDL / CSIR", "INDIA"),
        "ministry": ("Ministry of AYUSH", "INDIA"),
    }
    doc_type_map = {
        "act": "act",
        "rule": "rule",
        "rules": "rule",
        "guideline": "guideline",
        "guidelines": "guideline",
        "guide": "guideline",
        "treaty": "treaty",
        "circular": "circular",
        "faq": "faq",
        "form": "form",
        "manual": "manual",
    }

    authority, jurisdiction = "IP India", "INDIA"
    for p in parts:
        if p in authority_map:
            authority, jurisdiction = authority_map[p]
            break

    doc_type = next((doc_type_map[p] for p in parts if p in doc_type_map), "guideline")
    year = next((p for p in parts if re.match(r"^20\d{2}$", p)), "2024")

    title_words = [
        p.capitalize()
        for p in parts
        if p not in authority_map and p not in doc_type_map and not re.match(r"^20\d{2}$", p)
    ]
    title = " ".join(title_words) if title_words else filepath.stem

    return {
        "authority": authority,
        "jurisdiction": jurisdiction,
        "document_type": doc_type,
        "source_type": doc_type,
        "publication_date": year,
        "effective_date": f"{year}-01-01",
        "document_version": f"{year} Gazette Edition",
        "document_title": title,
        "filename": filepath.name,
        "topic": " ".join(title_words[:2]).lower() if title_words else "general",
        "language": "en",
        "source_url": "",
    }


def load_sidecar(filepath: Path) -> Dict[str, Any]:
    sidecar = filepath.with_suffix(".json")
    if not sidecar.exists():
        return {}
    import json
    try:
        with open(sidecar, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load sidecar {sidecar}: {e}")
        return {}


# ---------------------------------------------------------------------------
# Main ingestion loop
# ---------------------------------------------------------------------------

async def ingest(
    pdf_dir: Path,
    chunk_size: int = 600,
    overlap: int = 90,
    force: bool = False,
) -> None:
    """Run the full ingestion pipeline."""
    await init_db()

    pdf_files = sorted(pdf_dir.rglob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {pdf_dir}. Add PDFs and re-run.")
        return

    logger.info(f"Found {len(pdf_files)} PDFs in {pdf_dir}")

    async with AsyncSessionLocal() as db:
        total_chunks = 0

        for pdf_path in pdf_files:
            logger.info(f"\n📄 Processing: {pdf_path.name}")

            file_meta = metadata_from_filename(pdf_path)
            sidecar = load_sidecar(pdf_path)
            merged_meta = {**file_meta, **sidecar}

            try:
                with open(pdf_path, "rb") as f:
                    file_bytes = f.read()
                text, page_count = extract_text_from_pdf(file_bytes)
            except Exception as e:
                logger.error(f"  ❌ Extraction failed: {e}")
                continue

            if not text.strip():
                logger.warning(f"  ⚠️  No text extracted from {pdf_path.name} — skipping.")
                continue

            logger.info(f"  ✅ Extracted {len(text):,} chars from {page_count} pages.")

            source_id = hashlib.sha256(pdf_path.name.encode()).hexdigest()[:16]
            existing = await db.get(Source, source_id)
            if existing and not force:
                logger.info(f"  ℹ️  Source already in DB — skipping (use --force to re-ingest).")
            else:
                if existing:
                    await db.delete(existing)
                    await db.flush()
                source = Source(
                    id=source_id,
                    title=merged_meta.get("document_title") or merged_meta.get("title", pdf_path.stem),
                    url=merged_meta.get("source_url") or merged_meta.get("url", ""),
                    authority=merged_meta.get("authority", "Official Source"),
                    document_type=merged_meta.get("document_type", "guideline"),
                    jurisdiction=merged_meta.get("jurisdiction", "INDIA"),
                    topic=merged_meta.get("topic", "general"),
                    language=merged_meta.get("language", "en"),
                    publication_date=merged_meta.get("publication_date"),
                    document_version=merged_meta.get("document_version"),
                    effective_date=merged_meta.get("effective_date"),
                )
                db.add(source)
                await db.flush()

            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            logger.info(f"  📦 {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")

            chunk_ids = [f"{source_id}_{i}" for i in range(len(chunks))]
            chunk_meta: List[Dict[str, Any]] = []

            for i, chunk in enumerate(chunks):
                sec, rule, art = detect_section_or_rule(chunk)
                # Estimate page number proportionally
                approx_page = max(1, int((i / max(1, len(chunks))) * page_count) + 1)

                chunk_meta.append({
                    "source_id": source_id,
                    "id": f"{source_id}_{i}",
                    "source_url": merged_meta.get("source_url") or merged_meta.get("url", ""),
                    "document_title": merged_meta.get("document_title") or merged_meta.get("title", pdf_path.stem),
                    "document_type": merged_meta.get("document_type", "guideline"),
                    "source_type": merged_meta.get("document_type", "guideline"),
                    "authority": merged_meta.get("authority", "Official Source"),
                    "jurisdiction": merged_meta.get("jurisdiction", "INDIA"),
                    "section": sec,
                    "rule": rule,
                    "article": art,
                    "page_number": approx_page,
                    "publication_date": merged_meta.get("publication_date", ""),
                    "document_version": merged_meta.get("document_version", ""),
                    "effective_date": merged_meta.get("effective_date", ""),
                    "topic": merged_meta.get("topic", "general"),
                    "language": merged_meta.get("language", "en"),
                    "chunk_index": i,
                })

            add_documents(ids=chunk_ids, texts=chunks, metadatas=chunk_meta)
            total_chunks += len(chunks)
            logger.info(f"  ✅ Upserted {len(chunks)} chunks for {pdf_path.name}")

        await db.commit()

    logger.info(f"\n🎉 Ingestion complete. Total chunks upserted: {total_chunks}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IP-SAKTI Sahayak — KB ingestion script")
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing PDFs to ingest (default: data)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=600,
        help="Target chunk size in words (default: 600 ≈ 750 tokens)",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=90,
        help="Overlap between chunks in words (default: 90 ≈ 15%%)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest even if the source is already in the DB",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.pdf_dir.exists():
        logger.error(f"PDF directory not found: {args.pdf_dir}")
        sys.exit(1)
    asyncio.run(
        ingest(
            pdf_dir=args.pdf_dir,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            force=args.force,
        )
    )
