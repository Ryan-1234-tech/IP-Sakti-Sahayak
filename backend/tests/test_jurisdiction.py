"""
test_jurisdiction.py — Verifies Step 4: India vs International Jurisdiction Separation.
"""
import asyncio
import pytest
from app.services.vector_store import similarity_search
from app.services.rag import answer_query
from app.models.schemas import ChatRequest


def test_vector_search_india_jurisdiction():
    results = similarity_search("Patent application Form 1 and Form 2", top_k=3, jurisdiction="INDIA")
    for r in results:
        assert r.jurisdiction in ["INDIA", "GLOBAL"]


def test_vector_search_international_jurisdiction():
    results = similarity_search("Patent Cooperation Treaty PCT national phase deadline", top_k=3, jurisdiction="INTERNATIONAL")
    for r in results:
        assert r.jurisdiction in ["INTERNATIONAL", "GLOBAL"]


def test_chat_response_jurisdiction_tag():
    req_india = ChatRequest(query="What is the rule for patent application Form 18 in India?", jurisdiction="INDIA")
    res_india = asyncio.run(answer_query(req_india))
    assert res_india.jurisdiction == "INDIA"

    req_intl = ChatRequest(query="What is the 30 month deadline under PCT Article 22?", jurisdiction="INTERNATIONAL")
    res_intl = asyncio.run(answer_query(req_intl))
    assert res_intl.jurisdiction == "INTERNATIONAL"
