"""
test_source_cited_rag.py — Verifies Step 3: Source-Cited RAG Pipeline.
"""
import asyncio
import pytest
from app.models.schemas import SourceRef, ChatRequest, ChatResponse
from app.services.vector_store import RetrievedChunk, similarity_search
from app.services.rag import answer_query


def test_retrieved_chunk_metadata_preservation():
    chunk = RetrievedChunk(
        chunk_id="chunk-patent-act-sec3p-1",
        text="Section 3(p) excludes an invention which in effect is traditional knowledge.",
        score=0.92,
        metadata={
            "source_id": "indian-patents-act-1970",
            "document_title": "The Patents Act, 1970 (Act No. 39 of 1970)",
            "authority": "Indian Patent Office / Ministry of Commerce and Industry",
            "source_type": "statute",
            "jurisdiction": "INDIA",
            "section": "Section 3(p)",
            "article": None,
            "rule": None,
            "page_number": 14,
            "document_version": "2024 Amendment",
            "effective_date": "1972-04-20",
            "source_url": "https://ipindia.gov.in/patents-act.htm",
        }
    )
    
    assert chunk.source_id == "indian-patents-act-1970"
    assert chunk.authority == "Indian Patent Office / Ministry of Commerce and Industry"
    assert chunk.jurisdiction == "INDIA"
    assert chunk.section == "Section 3(p)"
    assert chunk.page_number == 14
    assert chunk.document_version == "2024 Amendment"
    assert chunk.effective_date == "1972-04-20"
    assert chunk.source_url == "https://ipindia.gov.in/patents-act.htm"


def test_rag_provenance_and_citations():
    query = "What is Section 3(p) under the Indian Patents Act?"
    req = ChatRequest(query=query, jurisdiction="INDIA", language="en")
    
    response = asyncio.run(answer_query(req))
    
    assert isinstance(response, ChatResponse)
    assert response.confidence in ["HIGH", "MEDIUM", "LOW"]
    assert len(response.sources) > 0
    
    first_src = response.sources[0]
    assert first_src.title is not None
    assert first_src.jurisdiction in ["INDIA", "INTERNATIONAL", "GLOBAL"]


def test_safe_abstention_on_empty_unsupported_query():
    query = "xyzqwerty123456789 non-existent alien biological formula on Mars galaxy"
    req = ChatRequest(query=query, jurisdiction="INDIA", language="en")
    
    response = asyncio.run(answer_query(req))
    
    assert response.confidence in ["MEDIUM", "LOW"]
    if response.abstained:
        assert "couldn't establish a reliable answer" in response.answer or "insufficient" in (response.abstention_reason or "").lower()
