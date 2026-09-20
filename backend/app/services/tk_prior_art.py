"""
services/tk_prior_art.py — Step 7: Traditional Knowledge / TKDL & Prior-Art Assistance Workflow.

Features:
  - Searches authentic indexed corpus of AYUSH guidelines, gazettes, and pharmacopoeias.
  - Transparent pointers for external/restricted databases (CSIR TKDL, IPO InPASS, WIPO Patentscope).
  - Strict compliance with truthful discovery: Never asserts "No prior art exists".
    Uses "No relevant record was identified in the sources searched."
  - Adds standard non-legal opinion disclaimer.
"""
from __future__ import annotations

import logging
from typing import List

from app.models.schemas import (
    PriorArtPointer,
    SourceRef,
    TKPriorArtRequest,
    TKPriorArtResponse,
)
from app.services.confidence import score_confidence
from app.services.vector_store import RetrievedChunk, similarity_search

logger = logging.getLogger(__name__)

# Transparent Official External Database Pointers
OFFICIAL_DATABASE_POINTERS: List[PriorArtPointer] = [
    PriorArtPointer(
        database_name="CSIR Traditional Knowledge Digital Library (TKDL)",
        access_type="Restricted / Institutional Access",
        search_url="https://www.tkdl.res.in",
        recommended_search_strategy="Search classical Sanskrit/Arabic/Tamil terms, botanical binomials (e.g. 'Withania somnifera'), and therapeutic indications (Rasayana, Jwara, Kandu) across the 54 recognized pharmacopoeias.",
        access_note="Direct TKDL database access is restricted to International Patent Offices under confidentiality agreements and authorized institutional research bodies. Independent applicants can conduct prior-art verification through the Ayurvedic Pharmacopoeia of India (API) Part I & II and published classical samhitas."
    ),
    PriorArtPointer(
        database_name="Indian Patent Advanced Search System (InPASS)",
        access_type="Public / Open Access",
        search_url="https://ipindiaservices.gov.in/publicsearch",
        recommended_search_strategy="Search Title & Abstract for ingredient combinations, Class A61K36 (Medicinal preparations of undetermined constitution from plants), and filter by Section 3(p) objections in published First Examination Reports (FER).",
        access_note="Full open-access public search portal provided by the Controller General of Patents, Designs and Trade Marks (CGPDTM), Government of India."
    ),
    PriorArtPointer(
        database_name="WIPO PATENTSCOPE (Global Patent Search)",
        access_type="Public / Open Access",
        search_url="https://patentscope.wipo.int",
        recommended_search_strategy="Search IPC Class A61K36 with Boolean operators for active fractions and English/Latin species names across all PCT international applications.",
        access_note="Free international patent database maintained by the World Intellectual Property Organization (WIPO)."
    ),
]


async def search_tk_prior_art(payload: TKPriorArtRequest) -> TKPriorArtResponse:
    """
    Execute authentic prior-art discovery against indexed corpus and formulate honest pointers.
    """
    search_query_parts = []
    if payload.formulation:
        search_query_parts.append(payload.formulation)
    if payload.ingredients:
        search_query_parts.append(payload.ingredients)
    if payload.traditional_use:
        search_query_parts.append(payload.traditional_use)
    if payload.therapeutic_claim:
        search_query_parts.append(payload.therapeutic_claim)
    if payload.keywords:
        search_query_parts.append(payload.keywords)

    combined_query = " ".join(search_query_parts).strip()
    if not combined_query:
        return TKPriorArtResponse(
            traditional_knowledge="Unable to determine",
            potential_prior_art="No search terms, formulation names, or ingredient keywords were provided.",
            retrieved_evidence=[],
            sources=[],
            database_pointers=OFFICIAL_DATABASE_POINTERS,
            next_step="Provide formulation name, ingredients, or traditional therapeutic claims to initiate search.",
            confidence="LOW",
            confidence_score=0.0,
            abstained=True,
            disclaimer="This is a prior-art discovery aid and not a legal opinion.",
        )

    # 1. Similarity search in available knowledge base
    chunks = similarity_search(
        f"Traditional Knowledge AYUSH prior art Section 3(p) {combined_query}",
        top_k=5,
        jurisdiction=payload.jurisdiction or "INDIA",
    )

    sources: List[SourceRef] = []
    seen = set()
    for c in chunks:
        sid = c.source_id or c.chunk_id
        if sid not in seen:
            seen.add(sid)
            sources.append(
                SourceRef(
                    id=sid,
                    source_id=c.source_id,
                    title=c.source_title,
                    authority=c.authority,
                    source_type=c.source_type,
                    jurisdiction=c.jurisdiction,
                    section=c.section,
                    article=c.article,
                    rule=c.rule,
                    page_number=c.page_number,
                    page=c.page_number,
                    url=c.source_url,
                    source_url=c.source_url,
                    relevance_score=round(c.score, 4),
                    relevance=round(c.score, 4),
                    snippet=c.text[:600],
                    chunk_id=c.chunk_id,
                )
            )

    # 2. Evaluate relevance thresholds
    relevant_chunks = [c for c in chunks if c.score >= 0.55]

    if relevant_chunks:
        tk_status = "Potential indication"
        prior_art_summary = (
            f"Identified {len(relevant_chunks)} potentially relevant authoritative record(s) with semantic overlap in the indexed knowledge base. "
            f"Top match: '{relevant_chunks[0].source_title}' (relevance {round(relevant_chunks[0].score * 100, 1)}%). "
            f"Examine cited provisions for potential Section 3(p) non-patentability exclusions."
        )
        next_step = "Review retrieved classical text citations and execute targeted novelty searches in InPASS and PATENTSCOPE using the recommended search strategies below."
    elif chunks:
        tk_status = "No relevant record identified in the sources searched"
        prior_art_summary = (
            "No relevant record was identified in the sources searched within the local knowledge base. "
            "This does NOT guarantee absence of prior art in the broader scientific literature or classical gazettes."
        )
        next_step = "Conduct a formal search in the Indian Patent Office InPASS database and consult the Ayurvedic Pharmacopoeia of India (API) Part I."
    else:
        tk_status = "No relevant record identified in the sources searched"
        prior_art_summary = "No relevant record was identified in the sources searched."
        next_step = "Execute full prior-art discovery across external patent registries using the pointers below."

    # 3. Confidence calculation
    conf = score_confidence(
        chunks=chunks,
        answer=prior_art_summary,
        jurisdiction=payload.jurisdiction or "INDIA",
    )

    return TKPriorArtResponse(
        traditional_knowledge=tk_status,
        potential_prior_art=prior_art_summary,
        retrieved_evidence=sources,
        sources=sources,
        database_pointers=OFFICIAL_DATABASE_POINTERS,
        next_step=next_step,
        confidence=conf.label,
        confidence_score=conf.score,
        abstained=False,
        disclaimer="This is a prior-art discovery aid and not a legal opinion.",
    )
