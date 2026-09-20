"""
test_tk_prior_art.py — Verifies Step 7: Traditional Knowledge / TKDL & Prior-Art Discovery Workflow.
"""
import asyncio
import pytest
from app.models.schemas import TKPriorArtRequest
from app.services.tk_prior_art import search_tk_prior_art


def test_tk_prior_art_discovery():
    req = TKPriorArtRequest(
        formulation="Topical turmeric and piperine wound healing formulation",
        ingredients="Curcuma longa (Turmeric), Piper nigrum (Black pepper)",
        traditional_use="Vranaropana in classical Ayurveda",
        therapeutic_claim="Synergistic wound healing and anti-inflammatory action",
        keywords="curcumin, piperine, wound healing, A61K 36/00",
        jurisdiction="INDIA",
    )
    res = asyncio.run(search_tk_prior_art(req))
    
    assert res.traditional_knowledge in [
        "Potential indication",
        "No relevant record identified in the sources searched"
    ]
    assert len(res.potential_prior_art) > 0
    
    # Check database pointers exist
    assert len(res.database_pointers) >= 3
    db_names = [p.database_name for p in res.database_pointers]
    assert any("TKDL" in name for name in db_names)
    assert any("InPASS" in name for name in db_names)
    assert any("PATENTSCOPE" in name for name in db_names)
    
    # Check honest disclaimer
    assert "guidance" in res.disclaimer.lower() or "discovery aid" in res.disclaimer.lower()
    assert "No prior art exists" not in res.potential_prior_art
