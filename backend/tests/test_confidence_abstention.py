"""
test_confidence_abstention.py — Verifies Step 8: Evidence-Based Confidence Scoring & Safe Abstention.
"""
import pytest
from app.services.vector_store import RetrievedChunk
from app.services.confidence import score_confidence, evaluate_abstention, build_abstention_response


def test_confidence_scoring_high():
    chunks = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="Section 3(p) of the Patents Act excludes traditional knowledge from patentability.",
            score=0.95,
            metadata={
                "source_id": "indian-patents-act-1970",
                "document_title": "The Patents Act, 1970",
                "authority": "Indian Patent Office",
                "source_type": "statute",
                "jurisdiction": "INDIA",
                "section": "Section 3(p)",
                "page_number": 14,
                "source_url": "https://ipindia.gov.in",
            }
        ),
        RetrievedChunk(
            chunk_id="chunk-2",
            text="Rule 18 of Biological Diversity Rules requires Form III approval from National Biodiversity Authority.",
            score=0.90,
            metadata={
                "source_id": "biological-diversity-act-2002",
                "document_title": "Biological Diversity Act, 2002",
                "authority": "National Biodiversity Authority",
                "source_type": "statute",
                "jurisdiction": "INDIA",
                "section": "Section 6",
                "page_number": 8,
                "source_url": "http://nbaindia.org",
            }
        ),
        RetrievedChunk(
            chunk_id="chunk-3",
            text="General guidelines for patent examination in India.",
            score=0.88,
            metadata={
                "source_id": "patent-guidelines",
                "document_title": "Patent Examination Guidelines",
                "authority": "Indian Patent Office",
                "source_type": "guideline",
                "jurisdiction": "INDIA",
            }
        )
    ]
    answer = "Under Section 3(p) of the Patents Act, traditional knowledge is excluded from patentability. Rule 18 requires Form III."
    conf = score_confidence(chunks=chunks, answer=answer, jurisdiction="INDIA")
    assert conf.label in ["HIGH", "MEDIUM"]
    assert conf.score >= 3.0


def test_confidence_scoring_low_empty():
    conf = score_confidence(chunks=[], answer="", jurisdiction="INDIA")
    assert conf.label == "LOW"
    assert conf.abstained is True


def test_safe_abstention_evaluation():
    chunks = [
        RetrievedChunk(
            chunk_id="c-weak",
            text="Some unrelated random generic text with minimal legal relevance.",
            score=0.25,
            metadata={
                "source_id": "general-notes",
                "document_title": "General Notes",
                "authority": "Informal",
                "source_type": "guideline",
                "jurisdiction": "INDIA",
            }
        )
    ]
    should_abstain, reason, next_step = evaluate_abstention(chunks=chunks, query="Sample question")
    assert should_abstain is True
    assert "relevance" in reason.lower() or "insufficient" in reason.lower()


def test_safe_abstention_response_builder():
    abs_text = build_abstention_response(
        reason="No statutory references found in the indexed database.",
        searched_sources=["Indian Patents Act", "Biological Diversity Act 2002"],
        recommended_next_step="Consult official IP India gazette."
    )
    assert "couldn't establish a reliable answer" in abs_text
    assert "No statutory references" in abs_text
