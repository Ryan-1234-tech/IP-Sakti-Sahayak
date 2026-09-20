"""
test_abs_assessor.py — Verifies Step 6: Biological Resource & ABS Assessor under Biological Diversity Act 2002/2023.
"""
import asyncio
import pytest
from app.models.schemas import ABSAssessRequest
from app.services.abs_assessor import assess_abs_compliance


def test_indian_entity_abs_assessment():
    req = ABSAssessRequest(
        biological_resource_used=True,
        resource_name="Curcuma longa & Withania somnifera",
        source_location="Western Ghats, Kerala",
        is_indian_origin=True,
        traditional_knowledge_associated=True,
        intended_use="Commercial IP / Patent Filing in India",
        commercialization_intent=True,
        user_entity_type="Indian MSME / Startup (100% Indian Shareholding)",
        jurisdiction="INDIA",
    )
    res = asyncio.run(assess_abs_compliance(req))
    assert "Biological resource" in res.biological_resource and "Curcuma" in res.biological_resource
    assert res.traditional_knowledge == "Yes"
    assert "Section 6" in res.relevant_framework or "Form III" in " ".join(res.next_steps)
    assert "ABS" in res.abs_review or "Indicated" in res.abs_review or "Mandatory" in res.abs_review or "Review indicated" in res.abs_review
    assert len(res.sources) > 0


def test_foreign_entity_section3_abs_assessment():
    req = ABSAssessRequest(
        biological_resource_used=True,
        resource_name="Bacopa monnieri",
        source_location="Wetlands of West Bengal",
        is_indian_origin=True,
        traditional_knowledge_associated=False,
        intended_use="Commercial Utilization & Global Patenting",
        commercialization_intent=True,
        user_entity_type="Foreign Corporation / Non-Resident Indian (Section 3 Entity)",
        jurisdiction="INDIA",
    )
    res = asyncio.run(assess_abs_compliance(req))
    assert "Section 3" in res.relevant_framework or "Form I" in " ".join(res.next_steps)
    assert res.confidence in ["HIGH", "MEDIUM"]


def test_non_biological_resource():
    req = ABSAssessRequest(
        biological_resource_used=False,
        resource_name="Synthetic Polymer Hydrogel",
        is_indian_origin=False,
        traditional_knowledge_associated=False,
        intended_use="Industrial Manufacturing",
        commercialization_intent=True,
        user_entity_type="Indian MSME / Startup (100% Indian Shareholding)",
        jurisdiction="INDIA",
    )
    res = asyncio.run(assess_abs_compliance(req))
    assert "No biological resource" in res.biological_resource
    assert res.traditional_knowledge == "No"
    assert "Not indicated" in res.abs_review or "No" in res.abs_review
