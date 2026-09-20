"""
services/rag.py — Source-Cited RAG Pipeline (Steps 3, 4, 8).

Key Features:
  - Preserves end-to-end statutory metadata from extraction to final response
  - Separates and filters by Jurisdiction (INDIA vs INTERNATIONAL)
  - Strict anti-hallucination citation verification
  - Evidence-based confidence scoring & safe abstention enforcement
  - Multi-lingual translation pipeline
"""
from __future__ import annotations

import json
import logging
import uuid
import re
from typing import List, Optional

from app.core.config import get_settings
from app.models.schemas import Action, ChatResponse, SourceRef
from app.services.confidence import (
    ConfidenceResult,
    build_abstention_response,
    score_confidence,
)
from app.services.language import (
    detect_language,
    normalize_language_code,
    translate_from_english,
    translate_to_english,
)
from app.services.llm import GROUNDING_SYSTEM_PROMPT, complete, complete_json
from app.services.vector_store import RetrievedChunk, similarity_search

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================
# Prompt building with full metadata preservation
# ============================================================


def _build_grounded_prompt(
    query_en: str,
    chunks: List[RetrievedChunk],
    jurisdiction: str = "INDIA",
) -> str:
    """
    Build the user-facing prompt that injects retrieved evidence chunks with full statutory provenance.
    The LLM is strictly instructed to answer ONLY from this evidence.
    """
    if not chunks:
        evidence_block = "No relevant authoritative evidence was found in the knowledge base for this query."
    else:
        evidence_parts = []
        for i, chunk in enumerate(chunks, start=1):
            source_label = chunk.source_title or "Official Source"
            authority = chunk.authority or "Official Authority"
            jur = chunk.jurisdiction
            sec_art_rule = chunk.section or chunk.article or chunk.rule or "General Provision"
            page_str = f"Page {chunk.page_number}" if chunk.page_number else "N/A"
            url = chunk.source_url or "N/A"

            meta_line = (
                f"Source [{i}]: {source_label}\n"
                f"Authority: {authority} | Jurisdiction: {jur}\n"
                f"Section/Article/Rule: {sec_art_rule} | {page_str}\n"
                f"URL: {url}"
            )
            snippet = chunk.text[:700] if len(chunk.text) > 700 else chunk.text
            evidence_parts.append(f"[Evidence {i}]\n{meta_line}\n\nContent:\n{snippet}")

        evidence_block = "\n\n---\n\n".join(evidence_parts)

    jur_instruction = (
        f"Jurisdiction Context: {jurisdiction.upper()}.\n"
        f"For INDIA: Prioritize Indian statutes (Patents Act 1970, Trade Marks Act 1999, Biological Diversity Act 2002, AYUSH guidelines).\n"
        f"For INTERNATIONAL: Treat international treaties (PCT, TRIPS, Paris Convention, WIPO) separately and never present an international treaty as an Indian domestic statute."
    )

    return (
        f"{jur_instruction}\n\n"
        f"EVIDENCE (use ONLY the following authoritative evidence to answer the question):\n\n"
        f"{evidence_block}\n\n"
        f"---\n\n"
        f"QUESTION: {query_en}\n\n"
        f"STRICT CITATION RULES:\n"
        f"1. Answer ONLY from the above evidence.\n"
        f"2. Cite the exact source title and section/article/rule for every statement (e.g. 'According to [Source Title], Section X...').\n"
        f"3. Do NOT invent, extrapolate, or cite sources not listed in the evidence above.\n"
        f"4. If the evidence is insufficient to answer the question reliably, explicitly state: 'The available authoritative sources do not contain sufficient evidence to fully address this query.'\n"
        f"5. End with numbered concrete Next Steps if supported by the evidence."
    )


# ============================================================
# Action extraction
# ============================================================


def _extract_actions(answer: str) -> List[Action]:
    """Parse next steps from the answer into structured Action objects."""
    regex_actions: List[Action] = []
    lines = answer.split("\n")
    for line in lines:
        line_s = line.strip()
        m = re.match(r"^(?:Step\s*)?(\d+)[\.\:\)]\s*(.*)", line_s, re.IGNORECASE)
        if m:
            step_num = int(m.group(1))
            desc = m.group(2).strip()
            if desc and len(desc) > 5 and not desc.lower().startswith("information provided"):
                regex_actions.append(Action(step=step_num, description=desc, required_documents=[]))

    if regex_actions:
        return regex_actions[:5]

    return []


# ============================================================
# Intent Routing & Source Prioritization
# ============================================================


def detect_query_intent(query: str) -> str:
    """Classify user query intent into statutory domain categories."""
    q = query.lower()
    if any(k in q for k in ["deadline", "due date", "expiry", "time limit", "days left"]):
        return "DEADLINE"
    elif any(k in q for k in ["ayush", "ayurved", "siddha", "unani", "herb", "turmeric", "ashwagandha", "neem"]):
        return "AYUSH"
    elif any(k in q for k in ["tkdl", "traditional knowledge", "prior art", "section 3(p)"]):
        return "TRADITIONAL_KNOWLEDGE"
    elif any(k in q for k in ["biological", "nba", "biodiversity", "form iii", "abs"]):
        return "BIOLOGICAL_MATERIAL"
    elif any(k in q for k in ["patentability", "novelty", "inventive step", "section 3(d)", "patentable"]):
        return "PATENTABILITY"
    elif any(k in q for k in ["trademark", "brand", "logo", "class 5", "tm-a"]):
        return "TRADEMARK"
    elif any(k in q for k in ["copyright", "manual", "artwork", "literary"]):
        return "COPYRIGHT"
    elif any(k in q for k in ["design", "bottle shape", "visual appearance"]):
        return "DESIGN"
    elif any(k in q for k in ["gi", "geographical indication"]):
        return "GI"
    elif any(k in q for k in ["section", "act", "provision", "rule", "law"]):
        return "LEGAL_EXPLANATION"
    return "GENERAL_IP"


def prioritize_chunks(chunks: List[RetrievedChunk], jurisdiction: str = "INDIA") -> List[RetrievedChunk]:
    """
    Sort retrieved chunks according to authority hierarchy & jurisdiction.
    """
    target_jur = jurisdiction.upper()

    def priority_score(chunk: RetrievedChunk) -> int:
        score = 0
        dt = (chunk.source_type or "").lower()
        title = (chunk.source_title or "").lower()

        # Jurisdiction match priority
        if chunk.jurisdiction.upper() == target_jur:
            score += 20

        # Authority hierarchy
        if "act" in dt or "act" in title:
            score += 10
        elif "rule" in dt or "rules" in title:
            score += 9
        elif "guideline" in dt or "guidelines" in title:
            score += 8
        elif "manual" in dt or "manuals" in title:
            score += 7
        elif "treaty" in dt or "convention" in title:
            score += 7
        elif "form" in dt or "notice" in title:
            score += 6
        elif "faq" in dt:
            score += 4
        else:
            score += 5

        return score

    return sorted(chunks, key=lambda c: (priority_score(c), c.score), reverse=True)


# ============================================================
# Main RAG execution function
# ============================================================


async def answer_query(
    query: Any,
    language: Optional[str] = None,
    conversation_id: Optional[str] = None,
    extra_context: Optional[str] = None,
    jurisdiction: Optional[str] = "INDIA",
) -> ChatResponse:
    """
    Full source-cited RAG pipeline with jurisdiction filtering, citation mapping,
    and safe abstention enforcement.
    """
    if hasattr(query, "query"):
        if language is None:
            language = getattr(query, "language", None)
        if conversation_id is None:
            conversation_id = getattr(query, "conversation_id", None)
        if jurisdiction is None or jurisdiction == "INDIA":
            jurisdiction = getattr(query, "jurisdiction", jurisdiction)
        query = str(query.query)

    jur = (jurisdiction or "INDIA").upper()

    # 1. Detect language
    detected_lang = normalize_language_code(language or detect_language(query))

    # 2. Translate query to English for retrieval
    query_en = translate_to_english(query, detected_lang)

    # 3. Retrieve & Prioritize chunks with jurisdiction awareness
    raw_chunks = similarity_search(
        query=query_en,
        top_k=settings.retrieval_top_k,
        jurisdiction=jur,
    )
    chunks = prioritize_chunks(raw_chunks, jurisdiction=jur)

    # 4. Check for Safe Abstention (Step 8)
    # If no chunks retrieved or top score is very weak
    if not chunks or chunks[0].score < 0.40:
        abstention_text = build_abstention_response(
            reason=f"No authoritative {jur} legal or regulatory documents matching this query were found in the knowledge base.",
            searched_sources=[f"{jur} Statutory Knowledge Base", "Official IP & AYUSH Gazettes"],
            recommended_next_step="Try rephrasing with specific statutory provisions or consult an official IP facilitator.",
        )
        answer_final = translate_from_english(abstention_text, detected_lang)
        conv_id = conversation_id or str(uuid.uuid4())
        msg_id = str(uuid.uuid4())

        return ChatResponse(
            message_id=msg_id,
            conversation_id=conv_id,
            answer=answer_final,
            sources=[],
            citations=[],
            confidence="LOW",
            confidence_score=0.0,
            abstained=True,
            abstention_reason="No supporting authoritative sources retrieved.",
            human_facilitator_available=True,
            actions=[],
            detected_language=detected_lang,
            jurisdiction=jur,
        )

    # 5. Build grounded prompt
    full_query = query_en
    if extra_context:
        full_query = f"Document context:\n{extra_context[:2000]}\n\nUser question: {query_en}"

    grounded_prompt = _build_grounded_prompt(full_query, chunks, jurisdiction=jur)

    # 6. LLM Call
    raw_answer_en = complete(grounded_prompt, system_prompt=GROUNDING_SYSTEM_PROMPT)

    # 7. Confidence & Safe Abstention Evaluation
    if raw_answer_en.startswith("[Error") or "error communicating" in raw_answer_en.lower():
        confidence_result = ConfidenceResult(
            label="LOW",
            score=0.0,
            reasons=["LLM backend unavailable or errored during inference"],
            abstained=True,
            abstention_reason="Unable to generate grounded LLM synthesis. Consult authoritative sources directly.",
            recommended_next_step="Review the cited primary legal sources attached below.",
            human_facilitator_available=True,
        )
    else:
        confidence_result = score_confidence(
            chunks=chunks,
            answer=raw_answer_en,
            jurisdiction=jur,
        )

    if confidence_result.abstained:
        answer_en = build_abstention_response(
            reason=confidence_result.abstention_reason or "Insufficient authoritative evidence.",
            searched_sources=[c.source_title for c in chunks[:3]],
            recommended_next_step=confidence_result.recommended_next_step,
        )
    else:
        answer_en = raw_answer_en

    # 8. Translate answer back
    answer_final = translate_from_english(answer_en, detected_lang)

    # 9. Extract actions
    actions = _extract_actions(answer_en) if not confidence_result.abstained else []

    # 10. Assemble structured citations strictly mapped to retrieved chunks
    citations: List[SourceRef] = []
    seen_ids: set[str] = set()
    for chunk in chunks:
        sid = chunk.source_id or chunk.chunk_id
        if sid in seen_ids:
            continue
        seen_ids.add(sid)
        citations.append(
            SourceRef(
                id=sid,
                source_id=chunk.source_id,
                title=chunk.source_title,
                authority=chunk.authority,
                source_type=chunk.source_type,
                document_type=chunk.source_type,
                jurisdiction=chunk.jurisdiction,
                section=chunk.section,
                article=chunk.article,
                rule=chunk.rule,
                page_number=chunk.page_number,
                page=chunk.page_number,
                document_version=chunk.document_version,
                effective_date=chunk.effective_date,
                url=chunk.source_url,
                source_url=chunk.source_url,
                relevance_score=round(chunk.score, 4),
                relevance=round(chunk.score, 4),
                snippet=chunk.text[:600],
                chunk_id=chunk.chunk_id,
            )
        )

    conv_id = conversation_id or str(uuid.uuid4())
    msg_id = str(uuid.uuid4())

    return ChatResponse(
        message_id=msg_id,
        conversation_id=conv_id,
        answer=answer_final,
        sources=citations,
        citations=citations,
        confidence=confidence_result.label,
        confidence_score=confidence_result.score,
        abstained=confidence_result.abstained,
        abstention_reason=confidence_result.abstention_reason,
        human_facilitator_available=True,
        actions=actions,
        detected_language=detected_lang,
        jurisdiction=jur,
    )
