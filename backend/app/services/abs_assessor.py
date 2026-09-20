"""
services/abs_assessor.py — Step 6: Biological Resource & ABS Assessor Engine.

Evaluates statutory obligations under the Biological Diversity Act 2002 (and 2023 Amendment):
  - Section 3: Prior approval of NBA for non-Indian entities / foreign participation
  - Section 4: Transfer of biological resource research results
  - Section 6: Prior approval of NBA (Form III) before grant of IPR
  - Section 7: Intimation to State Biodiversity Board (SBB) for Indian commercial entities
  - Access and Benefit Sharing (ABS) Guidelines 2014 calculation rates
"""
from __future__ import annotations

import logging
from typing import List, Optional

from app.models.schemas import ABSAssessRequest, ABSAssessResponse, SourceRef
from app.services.confidence import score_confidence
from app.services.vector_store import RetrievedChunk, similarity_search

logger = logging.getLogger(__name__)


async def assess_abs_compliance(payload: ABSAssessRequest) -> ABSAssessResponse:
    """
    Assess Biological Resource & Access and Benefit Sharing (ABS) regulatory compliance.
    """
    # 1. Check if Biological Resource is involved
    if not payload.biological_resource_used:
        return ABSAssessResponse(
            biological_resource="No biological resource involved in this application.",
            traditional_knowledge="No",
            abs_review="Not indicated — Biological Diversity Act 2002 obligations do not apply to purely synthetic or non-biological inventions.",
            relevant_framework="Not applicable.",
            next_steps=["Proceed with standard IP application procedures without NBA clearance."],
            sources=[],
            confidence="HIGH",
            confidence_score=5.0,
            abstained=False,
            disclaimer="Information provided for guidance only, not legal advice.",
        )

    # 2. Check for missing essential information
    res_name = (payload.resource_name or "").strip()
    if not res_name:
        return ABSAssessResponse(
            biological_resource="Biological resource usage indicated, but specific species/material name was not provided.",
            traditional_knowledge="Uncertain",
            abs_review="Unable to evaluate ABS exemptions or benefit-sharing obligations without specific biological resource identity and source details.",
            relevant_framework="Section 6 & Section 7, Biological Diversity Act 2002.",
            next_steps=[
                "Provide the specific botanical/zoological Latin binomial and common names of the biological resource.",
                "Specify the exact state/geographical location in India where the resource was collected.",
                "Specify whether cultivated or harvested from wild habitats."
            ],
            sources=[],
            confidence="LOW",
            confidence_score=1.0,
            abstained=True,
            abstention_reason="Missing biological resource species name and source origin details.",
            disclaimer="Information provided for guidance only, not legal advice.",
        )

    # 3. Analyze Entity Type & Jurisdiction Requirements
    entity = payload.user_entity_type.lower()
    is_foreign_entity = any(k in entity for k in ["foreign", "non-indian", "nri", "foreign shareholding", "foreign participation"])
    is_indian_origin = payload.is_indian_origin
    intended = payload.intended_use.lower()
    has_tk = payload.traditional_knowledge_associated or payload.associated_tk_details

    # Evaluate Relevant Statutory Framework
    framework_clauses: List[str] = []
    abs_clauses: List[str] = []
    next_steps: List[str] = []

    # Section 3 vs Section 7
    if is_foreign_entity and is_indian_origin:
        framework_clauses.append("Section 3(1), Biological Diversity Act 2002: Non-Indian entities and Indian companies with foreign equity MUST obtain prior approval from the National Biodiversity Authority (NBA, Chennai) via Form I before accessing any biological resource.")
        abs_clauses.append("Prior NBA approval (Form I) mandatory. Subject to standard Access and Benefit Sharing (ABS) agreement (0.1% to 0.5% of annual ex-factory gross sales or upfront percentage).")
        next_steps.append("File Form I with NBA, Chennai for prior permission to access Indian biological resources.")
    elif is_indian_origin:
        framework_clauses.append("Section 7, Biological Diversity Act 2002: Indian citizens and body corporates without foreign participation must give prior intimation to the concerned State Biodiversity Board (SBB) for commercial utilization.")
        abs_clauses.append("State Biodiversity Board (SBB) intimation indicated. Under ABS Guidelines 2014, Indian commercial entities contribute 0.1% to 0.5% of annual gross ex-factory sale value to the State Biodiversity Board.")
        next_steps.append("Submit prior intimation to the State Biodiversity Board (SBB) of the state where the biological resource was collected.")
    else:
        framework_clauses.append("Resources of Non-Indian origin accessed entirely outside India are exempt from Indian Biological Diversity Act 2002 provisions, provided official import documentation (bill of entry / phyto-sanitary certificate) is maintained.")
        abs_clauses.append("No ABS payment to Indian NBA indicated for purely imported foreign biological resources.")
        next_steps.append("Maintain customs import documentation, proof of foreign procurement, and phytosanitary clearance.")

    # Section 6 (IPR Applications)
    if "ipr" in intended or "patent" in intended or payload.commercialization_intent:
        if is_indian_origin:
            framework_clauses.append("Section 6(1), Biological Diversity Act 2002: Any person applying for any intellectual property right inside or outside India for any invention based on any research or information on a biological resource obtained from India MUST obtain prior approval of the NBA via Form III before the grant of the patent.")
            framework_clauses.append("Section 10(4)(d)(ii), Patents Act 1970: Mandatory declaration of source and geographical origin of biological material in Patent Form 1 & Complete Specification.")
            next_steps.append("File Form III with the National Biodiversity Authority (NBA) prior to the formal grant of patent by the Indian Patent Office (IPO).")
            next_steps.append("Declare the authentic geographical origin (State & District) in Clause 9(i) of Patent Form 1.")

    # Traditional Knowledge ABS Implications
    if has_tk:
        framework_clauses.append("Section 21(1), BDA 2002: Where biological resources are accessed with associated traditional knowledge, the NBA ensures fair and equitable benefit sharing directly with local communities / benefit claimers.")
        next_steps.append("Identify local tribal / community conservers if traditional knowledge was obtained from specific indigenous practitioners.")

    # 4. Grounded RAG Retrieval for NBA & ABS Guidelines
    chunks = similarity_search(
        f"Biological Diversity Act 2002 Section 6 Form III NBA Approval ABS Guidelines {res_name}",
        top_k=4,
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
                    authority=c.authority or "National Biodiversity Authority",
                    source_type=c.source_type,
                    jurisdiction=c.jurisdiction,
                    section=c.section or "Section 6",
                    article=c.article,
                    rule=c.rule or "Rule 18 BDA Rules 2004",
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

    # 5. Shared Confidence Scoring
    conf = score_confidence(
        chunks=chunks,
        answer=" ".join(framework_clauses),
        jurisdiction=payload.jurisdiction or "INDIA",
    )

    bio_summary = (
        f"Biological resource '{res_name}' declared ({'Indian origin' if is_indian_origin else 'Foreign/Imported origin'}). "
        f"Source Location: {payload.source_location or 'India'}. Intended Use: {payload.intended_use}."
    )

    return ABSAssessResponse(
        biological_resource=bio_summary,
        traditional_knowledge="Yes" if has_tk else "No",
        abs_review="\n\n".join(abs_clauses),
        relevant_framework="\n\n".join(framework_clauses),
        next_steps=next_steps,
        sources=sources,
        confidence=conf.label,
        confidence_score=conf.score,
        abstained=False,
        disclaimer="Information provided for guidance only, not legal advice.",
    )
