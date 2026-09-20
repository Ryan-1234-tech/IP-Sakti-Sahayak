"""
routers/sources.py — GET /api/sources
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db import Source
from app.models.schemas import SourceListItem, SourcesResponse
from app.services.vector_store import collection_count

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sources", response_model=SourcesResponse, summary="List all knowledge-base sources")
async def list_sources(
    jurisdiction: Optional[str] = Query(None, description="INDIA | INTERNATIONAL"),
    db: AsyncSession = Depends(get_db),
) -> SourcesResponse:
    """
    Return a list of all curated knowledge-base sources, optionally filtered by jurisdiction.
    """
    stmt = select(Source).order_by(Source.authority, Source.title)
    if jurisdiction:
        stmt = stmt.where(Source.jurisdiction == jurisdiction.upper())

    result = await db.execute(stmt)
    db_sources = result.scalars().all()

    if not db_sources:
        items = _demo_sources(jurisdiction)
    else:
        items = [
            SourceListItem(
                id=s.id,
                title=s.title,
                authority=s.authority,
                url=s.url,
                document_type=s.document_type,
                jurisdiction=s.jurisdiction,
                topic=s.topic,
                publication_date=s.publication_date,
            )
            for s in db_sources
        ]

    chunk_count = collection_count()
    logger.info(f"Returning {len(items)} sources ({chunk_count} total chunks in KB).")

    return SourcesResponse(sources=items, total=len(items))


def _demo_sources(jurisdiction: Optional[str] = None) -> list[SourceListItem]:
    """Seed sources shown before KB ingestion."""
    all_demos = [
        SourceListItem(
            id="demo-1",
            title="Indian Patents Act 1970 & Patents Rules 2024",
            authority="IP India",
            url="https://ipindia.gov.in/patents.htm",
            document_type="act",
            jurisdiction="INDIA",
            topic="patents",
        ),
        SourceListItem(
            id="demo-2",
            title="Trade Marks Act 1999 & Trade Marks Rules 2017",
            authority="IP India",
            url="https://ipindia.gov.in/trade-marks.htm",
            document_type="act",
            jurisdiction="INDIA",
            topic="trademarks",
        ),
        SourceListItem(
            id="demo-3",
            title="Drugs & Cosmetics Act 1940 & AYUSH Rule 158B",
            authority="Ministry of AYUSH",
            url="https://ayush.gov.in/",
            document_type="rule",
            jurisdiction="INDIA",
            topic="AYUSH",
        ),
        SourceListItem(
            id="demo-4",
            title="Biological Diversity Act 2002 & NBA Form III Guidelines",
            authority="National Biodiversity Authority",
            url="http://nbaindia.org/",
            document_type="act",
            jurisdiction="INDIA",
            topic="biodiversity",
        ),
        SourceListItem(
            id="demo-5",
            title="PCT International Patent System Guide",
            authority="WIPO",
            url="https://www.wipo.int/pct/en/",
            document_type="treaty",
            jurisdiction="INTERNATIONAL",
            topic="patents",
        ),
        SourceListItem(
            id="demo-6",
            title="WTO TRIPS Agreement on Intellectual Property",
            authority="WIPO",
            url="https://www.wto.org/english/tratop_e/trips_e/trips_e.htm",
            document_type="treaty",
            jurisdiction="INTERNATIONAL",
            topic="patents",
        ),
    ]
    if jurisdiction:
        jur = jurisdiction.upper()
        return [s for s in all_demos if s.jurisdiction == jur]
    return all_demos
