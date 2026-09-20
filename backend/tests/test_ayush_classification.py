"""
test_ayush_classification.py — Verifies Step 5: Guided AYUSH Formulation Classification (7 Classes).
"""
import asyncio
import pytest
from app.models.schemas import AYUSHClassifyRequest, IngredientInput
from app.services.ayush_classifier import classify_ayush_formulation


def test_classical_ayurvedic_classification():
    req = AYUSHClassifyRequest(
        formulation_name="Classical Chyawanprash",
        formulation_source="Classical Ayurvedic Text",
        authoritative_classical_text="Charaka Samhita",
        therapeutic_claims="Rasayana rejuvenation and natural immunity",
        ingredients=[
          IngredientInput(name="Amalaki", latin_name="Phyllanthus emblica", percentage=50),
          IngredientInput(name="Guduchi", latin_name="Tinospora cordifolia", percentage=50),
        ],
        biological_materials_used=True,
        jurisdiction="INDIA",
    )
    res = asyncio.run(classify_ayush_formulation(req))
    assert "Classical" in res.product_classification
    assert res.traditional_knowledge == "Yes"
    assert res.tkdl_prior_art == "Recommended"
    assert res.confidence in ["HIGH", "MEDIUM"]


def test_phytopharmaceutical_classification():
    req = AYUSHClassifyRequest(
        formulation_name="Standardized Withanolide-A Bioactive Fraction",
        formulation_source="Purified Active Botanical Fraction",
        therapeutic_claims="Phase I/II clinical trial validated neuroprotection",
        ingredients=[
          IngredientInput(name="Standardized Withanolide-A Fraction (98% purity)", latin_name="Withania somnifera", percentage=100, is_novel=True),
        ],
        novel_ingredients=["Withanolide-A Fraction"],
        biological_materials_used=True,
        jurisdiction="INDIA",
    )
    res = asyncio.run(classify_ayush_formulation(req))
    assert "Phytopharmaceutical" in res.product_classification
    assert res.biological_resource == "Yes"
    assert res.confidence in ["HIGH", "MEDIUM"]


def test_patent_proprietary_classification():
    req = AYUSHClassifyRequest(
        formulation_name="GlycoShield Proprietary Syrup",
        formulation_source="In-House R&D",
        authoritative_classical_text="None / Proprietary R&D",
        therapeutic_claims="Synergistic glucose regulation ratio",
        ingredients=[
          IngredientInput(name="Gymnema", percentage=50),
          IngredientInput(name="Vijaysar", percentage=50),
        ],
        biological_materials_used=True,
        jurisdiction="INDIA",
    )
    res = asyncio.run(classify_ayush_formulation(req))
    assert "Patent" in res.product_classification or "Proprietary" in res.product_classification


def test_ayurveda_aahar_classification():
    req = AYUSHClassifyRequest(
        formulation_name="Ayurveda Golden Elixir Tea",
        formulation_source="Dietary Food Recipe",
        therapeutic_claims="Daily dietary wellness and food supplement nutrition",
        product_type="Food / Beverage",
        ingredients=[
          IngredientInput(name="Turmeric Powder", percentage=50),
          IngredientInput(name="Ginger", percentage=50),
        ],
        biological_materials_used=True,
        jurisdiction="INDIA",
    )
    res = asyncio.run(classify_ayush_formulation(req))
    assert "Ayurveda-Aahar" in res.product_classification or "Dietary" in res.product_classification or "Proprietary" in res.product_classification


def test_cosmetic_classification():
    req = AYUSHClassifyRequest(
        formulation_name="Herbal Glow Face Cream",
        formulation_source="Cosmetic Formulation",
        therapeutic_claims="External skin moisturization and beautification only with no disease treatment claims",
        product_type="Cosmetic",
        ingredients=[
          IngredientInput(name="Aloe vera", percentage=60),
          IngredientInput(name="Almond oil", percentage=40),
        ],
        biological_materials_used=True,
        jurisdiction="INDIA",
    )
    res = asyncio.run(classify_ayush_formulation(req))
    assert "Cosmetic" in res.product_classification


def test_insufficient_info_classification():
    req = AYUSHClassifyRequest(
        formulation_name="Unspecified Unknown Mixture",
        formulation_source=None,
        authoritative_classical_text=None,
        therapeutic_claims=None,
        ingredients=[],
        jurisdiction="INDIA",
    )
    res = asyncio.run(classify_ayush_formulation(req))
    assert "Insufficient" in res.product_classification
    assert res.confidence == "LOW"
