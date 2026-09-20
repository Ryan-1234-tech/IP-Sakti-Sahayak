"""
services/confidence.py — Shared Evidence-Based Confidence & Safe Abstention Service (Step 8).

Implements objective, verifiable scoring across all IP-SAKTI Sahayak modules:
  - Retrieval similarity
  - Corroborating source count
  - Source authority & primary statutory provenance
  - Jurisdiction alignment (INDIA vs INTERNATIONAL)
  - Evidence completeness & absence of contradictions
  - Missing user information detection

Safe Abstention:
  Triggers when evidence is insufficient, contradictory, out of scope,
  or missing essential inputs, returning a standardized, honest response.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import get_settings
from app.services.vector_store import RetrievedChunk

settings = get_settings()

# Phrases indicating model hedging or gaps in authoritative evidence
_HEDGE_PATTERNS = re.compile(
    r"(not (?:fully )?covered|cannot (?:fully )?answer|insufficient evidence|"
    r"please consult|not enough information|may not be accurate|"
    r"outside (?:the )?scope|i don'?t have|no information|unclear from|"
    r"could not find|no supporting source)",
    re.IGNORECASE,
)

# Standard safe abstention message prefix mandated across the system
ABSTENTION_HEADER = "I couldn't establish a reliable answer from the authoritative sources available to me."


@dataclass
class ConfidenceResult:
    label: str                   # HIGH | MEDIUM | LOW
    score: float                 # numeric score (0 to 5.0)
    reasons: List[str] = field(default_factory=list)
    abstained: bool = False
    abstention_reason: Optional[str] = None
    recommended_next_step: Optional[str] = None
    human_facilitator_available: bool = True


def evaluate_abstention(
    chunks: List[RetrievedChunk],
    query: str,
    answer: Optional[str] = None,
    jurisdiction: Optional[str] = "INDIA",
    missing_user_info: Optional[List[str]] = None,
    conflicting_sources: bool = False,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Determine if the system must safely abstain from giving a definitive legal conclusion.
    
    Returns:
        (abstained: bool, reason: str | None, next_step: str | None)
    """
    # 1. Missing essential user parameters
    if missing_user_info and len(missing_user_info) > 0:
        missing_str = ", ".join(missing_user_info)
        return (
            True,
            f"Missing required formulation/applicant information: {missing_str}.",
            "Please provide the missing details (such as ingredient botanical names, origin, or intended claims) and retry.",
        )

    # 2. No retrieved chunks or all chunks below minimal similarity threshold
    min_similarity_threshold = 0.40
    if not chunks:
        return (
            True,
            "No supporting statutory or regulatory documents were retrieved from the knowledge base for this query.",
            "Verify your query keywords or consult official IP India / Ministry of AYUSH publications directly.",
        )

    valid_chunks = [c for c in chunks if c.score >= min_similarity_threshold]
    if not valid_chunks:
        return (
            True,
            f"Retrieved candidate documents had insufficient semantic relevance (top score {chunks[0].score:.2f} < {min_similarity_threshold}).",
            "Try rephrasing your question using official statutory terms (e.g. Section 3(p), Form III, Class 5).",
        )

    # 3. Material conflict detected between retrieved sources
    if conflicting_sources:
        return (
            True,
            "Retrieved authoritative sources contain conflicting statutory provisions or differing state gazette rules.",
            "Request a case review with a certified Patent/AYUSH facilitator to evaluate the jurisdictional conflict.",
        )

    # 4. LLM explicitly self-reported complete lack of grounding
    if answer and ("no supporting source was retrieved" in answer.lower() or "outside the scope of indexed" in answer.lower()):
        return (
            True,
            "The query falls outside the indexed provisions of Indian Patent, Trademark, and AYUSH regulatory databases.",
            "Consult a registered patent attorney or refer directly to the Gazette of India.",
        )

    return False, None, None


def score_confidence(
    chunks: List[RetrievedChunk],
    answer: str,
    jurisdiction: Optional[str] = "INDIA",
    missing_user_info: Optional[List[str]] = None,
    conflicting_sources: bool = False,
) -> ConfidenceResult:
    """
    Compute a shared rule- and evidence-based confidence score.
    """
    # Check for safe abstention trigger first
    must_abstain, abs_reason, next_step = evaluate_abstention(
        chunks=chunks,
        query="",
        answer=answer,
        jurisdiction=jurisdiction,
        missing_user_info=missing_user_info,
        conflicting_sources=conflicting_sources,
    )

    if must_abstain:
        return ConfidenceResult(
            label="LOW",
            score=0.0,
            reasons=[f"Safe abstention triggered: {abs_reason}"],
            abstained=True,
            abstention_reason=abs_reason,
            recommended_next_step=next_step,
            human_facilitator_available=True,
        )

    score = 0
    reasons: List[str] = []
    target_jur = (jurisdiction or "INDIA").upper()

    # 1. Retrieval Similarity
    top_score = chunks[0].score if chunks else 0.0
    if top_score >= settings.similarity_threshold_high:
        score += 2
        reasons.append(f"+2: Top chunk similarity {top_score:.2f} ≥ threshold ({settings.similarity_threshold_high})")
    elif top_score >= 0.50:
        score += 1
        reasons.append(f"+1: Top chunk similarity {top_score:.2f} is moderate (≥ 0.50)")
    else:
        reasons.append(f"  0: Top chunk similarity {top_score:.2f} is low")

    # 2. Corroborating sources count
    if len(chunks) >= 3:
        score += 1
        reasons.append(f"+1: {len(chunks)} corroborating sources retrieved (≥3 sources)")
    elif len(chunks) >= 2:
        score += 1
        reasons.append(f"+1: {len(chunks)} corroborating sources retrieved (≥2 sources)")
    else:
        score -= 1
        reasons.append(" -1: Only 1 supporting chunk retrieved")

    # 3. Source Authority & Primary Provenance
    has_primary = any(c.is_primary_source for c in chunks)
    if has_primary:
        score += 1
        reasons.append("+1: At least one primary government statute/gazette cited")

    # 4. Jurisdiction Alignment
    matched_jur = any(c.jurisdiction.upper() == target_jur for c in chunks)
    if matched_jur:
        score += 1
        reasons.append(f"+1: Sourced citations match target jurisdiction ({target_jur})")
    else:
        score -= 1
        reasons.append(f" -1: Sourced citations mismatch target jurisdiction ({target_jur})")

    # 5. Penalize hedging / self-reported uncertainty
    if _HEDGE_PATTERNS.search(answer):
        score -= 1
        reasons.append(" -1: Answer contains hedging/provisional guidance language")

    # Map numeric score to label
    # Max possible score = 5.0, Min = 0.0
    normalized_score = max(0.0, min(5.0, float(score)))

    if normalized_score >= 4.0:
        label = "HIGH"
    elif normalized_score >= 2.0:
        label = "MEDIUM"
    else:
        label = "LOW"

    return ConfidenceResult(
        label=label,
        score=normalized_score,
        reasons=reasons,
        abstained=False,
        abstention_reason=None,
        recommended_next_step=None,
        human_facilitator_available=True,
    )


def build_abstention_response(
    reason: str,
    searched_sources: Optional[List[str]] = None,
    recommended_next_step: Optional[str] = None,
) -> str:
    """
    Generate the structured user-facing safe abstention message.
    """
    parts = [
        ABSTENTION_HEADER,
        "",
        f"**Reason:** {reason}",
    ]

    if searched_sources and len(searched_sources) > 0:
        sources_list = ", ".join(searched_sources[:4])
        parts.append(f"**Sources Searched:** {sources_list}")

    step = (
        recommended_next_step
        or "Consult the official publications of the Indian Patent Office, Ministry of AYUSH, or National Biodiversity Authority."
    )
    parts.append(f"**Recommended Next Step:** {step}")
    parts.append(
        "**Human Facilitator Option:** If you require binding statutory clearance, connect with an empanelled IP Facilitator or Registered Patent Agent."
    )

    return "\n".join(parts)
