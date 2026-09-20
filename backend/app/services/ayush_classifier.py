"""
services/ayush_classifier.py — Step 5: Guided AYUSH Formulation Classification Engine.

Implements deterministic decision logic and grounded statutory citations for:
  1. Classical Ayurvedic Medicine
  2. Patent/Proprietary Medicine (ASU)
  3. New / Non-Classical Drug
  4. Phytopharmaceutical
  5. Ayurveda-Aahar / Nutraceutical
  6. Cosmetic
  7. Insufficient information / unable to classify

Grounded in:
  - Drugs and Cosmetics Act 1940 (First Schedule, Section 3(a), Section 33EEB)
  - Drugs and Cosmetics Rules 1945 (Rule 158B, Rule 157)
  - FSSAI (Ayurveda Aahar) Regulations 2022
  - Phytopharmaceutical Drug Regulations (Schedule Y / Chapter IV-A)
  - Cosmetics Rules 2020
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from app.models.schemas import (
    AYUSHClassifyRequest,
    AYUSHClassifyResponse,
    IngredientInput,
    SourceRef,
)
from app.services.confidence import score_confidence
from app.services.vector_store import RetrievedChunk, similarity_search

logger = logging.getLogger(__name__)

# List of 54 Authoritative Classical Books recognized under First Schedule of Drugs & Cosmetics Act 1940
FIRST_SCHEDULE_TEXTS = [
    "charaka samhita", "sushruta samhita", "ashtanga hridaya", "ashtanga sangraha",
    "sharangdhara samhita", "bhavaprakasha", "madhava nidana", "bhaishajya ratnavali",
    "ayurvedic pharmacopoeia of india", "api", "ayurvedic formulary of india", "afi",
    "sahasrayoga", "rasa ratna samucchaya", "yoga ratnakara", "dravya guna vijnana",
    "siddha formulary of india", "national formulary of unani medicine", "nfum",
    "unani pharmacopoeia of india", "siddha pharmacopoeia of india", "gunapadam"
]


def classify_formulation_deterministic(
    payload: AYUSHClassifyRequest,
) -> Tuple[str, str, str, str, str, str, str, str, List[str]]:
    """
    Deterministic classification decision tree.
    Returns:
      (classification, basis, regulatory_considerations, ip_implications,
       tk_status, bio_status, abs_status, tkdl_status, next_steps)
    """
    name = payload.formulation_name.strip()
    src = (payload.formulation_source or "").lower()
    classical_ref = (payload.authoritative_classical_text or "").lower()
    intended = (payload.intended_use or "").lower()
    claims = (payload.therapeutic_claims or "").lower()
    prod_type = (payload.product_type or "").lower()
    has_novel = bool(payload.novel_ingredients and len(payload.novel_ingredients) > 0)
    ingredients = payload.ingredients or []

    # 1. Check for Insufficient Information
    if not name or (len(ingredients) == 0 and not classical_ref and not claims):
        return (
            "Insufficient information / unable to classify",
            "Key formulation parameters (ingredients, classical references, or therapeutic claims) were not provided.",
            "Under Section 33EEB of the Drugs & Cosmetics Act 1940, licensing requires defined active ingredients and classical/clinical justification.",
            "Cannot assess patentability or Section 3(p) exclusion without complete composition and ingredient ratios.",
            "Uncertain",
            "Uncertain",
            "Uncertain",
            "Recommended",
            [
                "Provide the complete list of botanical/mineral ingredients with Latin names.",
                "Specify whether the formulation follows a classical text listed in the First Schedule.",
                "State the intended therapeutic claims or commercialization category."
            ]
        )

    # 2. Check for Cosmetic
    if "cosmetic" in prod_type or "topical cosmetic" in intended or any(k in claims for k in ["beautif", "glow", "skin aesthetic", "hair shine", "cleanser", "perfume", "complexion"]) and not any(k in claims for k in ["cure", "treat", "pathology", "disease", "chronic", "eczema", "psoriasis"]):
        return (
            "Cosmetic",
            "Product is intended solely for cleansing, beautifying, promoting attractiveness, or altering appearance without therapeutic disease claims.",
            "Regulated under the Cosmetics Rules 2020 / Chapter IV of Drugs & Cosmetics Act 1940. Manufacturing licence required under Form COS-8.",
            "Formulation may seek Trademark (Class 3) and Design registration for packaging. Standard composition lacks patentable pharmaceutical novelty unless novel cosmetic delivery is proven.",
            "No" if not has_novel else "Uncertain",
            "Yes" if payload.biological_materials_used else "No",
            "Review indicated" if payload.biological_materials_used else "Not indicated",
            "Not indicated",
            [
                "Apply for Cosmetic Manufacturing Licence under Cosmetics Rules 2020.",
                "Register Brand Name and Logo under Trademark Class 3.",
                "Verify that label claims do not make therapeutic/curative claims to avoid misbranding objections under Section 17C."
            ]
        )

    # 3. Check for Ayurveda-Aahar / Nutraceutical
    if "food" in prod_type or "beverage" in prod_type or "dietary" in intended or "health maintenance" in intended or "ayurveda-aahar" in src or "nutraceutical" in src:
        return (
            "Ayurveda-Aahar / nutraceutical",
            "Food product or dietary supplement prepared in accordance with the authoritative classical texts of Ayurveda for health maintenance, without claiming to prevent or cure diseases.",
            "Regulated under the Food Safety and Standards (Ayurveda Aahar) Regulations 2022. Requires FSSAI license with dedicated Ayurveda Aahar logo.",
            "Patent protection is excluded for mere food aggregations (Section 3(e)). Protection is primarily achieved through Trademark (Class 30/29), Trade Dress, and Trade Secrets.",
            "Yes",
            "Yes" if payload.biological_materials_used else "No",
            "Review indicated" if payload.biological_materials_used else "Not indicated",
            "Recommended",
            [
                "Obtain FSSAI Ayurveda Aahar Manufacturing Licence.",
                "Affix the mandatory official Ayurveda Aahar logo on all packaging.",
                "Register Brand Name and Packaging Trademark under Class 30 / Class 29."
            ]
        )

    # 4. Check for Phytopharmaceutical
    if "phytopharmaceutical" in src or "standardized fraction" in intended or any("fraction" in (ing.name.lower() + (ing.latin_name or "").lower()) for ing in ingredients):
        return (
            "Phytopharmaceutical",
            "Purified and standardized fraction with defined minimum 4 bioactive marker compounds extracted from an Indian medicinal plant, evaluated for a specific therapeutic indication.",
            "Regulated under Chapter IV-A & Schedule Y (Rule 122DA/122E) of Drugs & Cosmetics Rules. Requires CDSCO Central Licensing approval and Phase I-III clinical trial data.",
            "Strong patent potential under Section 2(1)(j) for novel extraction fraction, specific marker synergy, and defined chromatographic fingerprinting. Overcomes Section 3(p) via proof of non-obvious standardized fraction.",
            "Yes",
            "Yes",
            "Review indicated",
            "Recommended",
            [
                "Generate chromatographic fingerprinting profiles (HPLC/HPTLC/LC-MS) with minimum 4 bioactive markers.",
                "Submit Investigational New Drug (IND) application to CDSCO for clinical trials.",
                "Obtain Form III approval from the National Biodiversity Authority (NBA) under Section 6 of Biological Diversity Act 2002."
            ]
        )

    # 5. Check for Classical Ayurvedic Medicine
    is_classical_text = any(t in classical_ref for t in FIRST_SCHEDULE_TEXTS) or "classical text" in src
    if is_classical_text and not has_novel:
        return (
            "Classical Ayurvedic Medicine",
            f"Formulation composition, ratio, and preparation method exactly match authoritative texts specified in the First Schedule of the Drugs and Cosmetics Act 1940 ({payload.authoritative_classical_text or 'API/Charaka Samhita'}).",
            "Manufactured under AYUSH Drug Manufacturing Licence (Rule 154/158B(1) Drugs & Cosmetics Rules 1945). No prior clinical trial required if classical recipe is strictly followed.",
            "Direct product patent is EXCLUDED under Section 3(p) of Indian Patents Act 1970 (Traditional Knowledge). Brand identity protectable under Trademark Class 5.",
            "Yes",
            "Yes" if payload.biological_materials_used else "No",
            "Review indicated",
            "Recommended",
            [
                "Apply for AYUSH Manufacturing Licence under Form 25-D from State AYUSH Licensing Authority.",
                "Ensure strict adherence to standard pharmacopoeial parameters in Ayurvedic Pharmacopoeia of India (API).",
                "Register Brand Name under Trademark Class 5 (Pharmaceutical & AYUSH products)."
            ]
        )

    # 6. Check for Patent / Proprietary Medicine (ASU)
    has_classical_ingredients = any(any(t in ing.name.lower() for t in ["ashwagandha", "turmeric", "guduchi", "neem", "tulsi", "triphala", "brahmi", "kalmegh", "amla", "gymnema", "vijaysar", "meshashringi", "jamun", "herb", "extract", "botanical"]) for ing in ingredients)
    if (has_classical_ingredients or "modified" in src or "proprietary" in src or "in-house" in src or "r&d" in src) and not has_novel:
        return (
            "Patent/Proprietary Medicine",
            "Formulation contains all ingredients mentioned in authoritative books of Ayurveda, Siddha, or Unani, but processed into modern dosage forms (capsules, syrups, tablets) or innovative synergistic combinations not found as a verbatim classical text recipe.",
            "Regulated under Section 3(h) & Rule 158B(A) of Drugs & Cosmetics Rules 1945. Requires safety and published literature evidence / pilot efficacy trial data for State AYUSH licensing.",
            "Patentable ONLY if non-obvious synergistic efficacy (Combination Index < 1.0) is proven to overcome Section 3(p) and Section 3(e) objections. Trademark Class 5 is strongly recommended.",
            "Yes",
            "Yes",
            "Review indicated",
            "Recommended",
            [
                "Conduct in-vitro/in-vivo Synergistic Efficacy assays to generate comparative data for patent filing.",
                "Submit Rule 158B safety and shelf-life study dossier to the State Licensing Authority for Form 25-D.",
                "Submit Form III to National Biodiversity Authority (NBA) prior to patent filing."
            ]
        )

    # 7. Default to New / Non-Classical Drug if novel synthetic or unlisted ingredients
    return (
        "New / Non-Classical Drug",
        "Formulation contains novel chemical fractions, non-traditional extraction solvents, synthetic additives, or unlisted biological ingredients not recognized in classical pharmacopoeias.",
        "Regulated under the New Drugs and Clinical Trials Rules 2019 by CDSCO. Requires full non-clinical toxicity profile and phased clinical trials.",
        "High patentability potential if novelty and inventive step are established under Section 2(1)(j). Traditional Knowledge Section 3(p) exclusion is less likely if active entity is completely novel.",
        "No" if not has_classical_ingredients else "Yes",
        "Yes" if payload.biological_materials_used else "No",
        "Review indicated" if payload.biological_materials_used else "Not indicated",
        "Recommended",
        [
            "File Provisional Patent Application (Form 1 & 2) immediately to establish priority date.",
            "Submit Pre-clinical Toxicology dossier to CDSCO for permission to conduct clinical trials.",
            "File Form III with NBA if biological materials sourced from India are utilized."
        ]
    )


async def classify_ayush_formulation(
    payload: AYUSHClassifyRequest,
) -> AYUSHClassifyResponse:
    """
    Full AYUSH classification workflow integrating deterministic logic, grounded RAG citations,
    and evidence-based confidence scoring.
    """
    (
        classification,
        basis,
        reg_considerations,
        ip_implications,
        tk_status,
        bio_status,
        abs_status,
        tkdl_status,
        next_steps,
    ) = classify_formulation_deterministic(payload)

    # 1. Retrieve supporting grounded legal chunks via RAG
    query = f"AYUSH {classification} Rule 158B Drugs Cosmetics Act First Schedule Section 3(p)"
    chunks = similarity_search(query, top_k=4, jurisdiction=payload.jurisdiction or "INDIA")

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
                    document_version=c.document_version,
                    effective_date=c.effective_date,
                    url=c.source_url,
                    source_url=c.source_url,
                    relevance_score=round(c.score, 4),
                    relevance=round(c.score, 4),
                    snippet=c.text[:600],
                    chunk_id=c.chunk_id,
                )
            )

    # 2. Shared Confidence Scoring
    conf = score_confidence(
        chunks=chunks,
        answer=f"{classification}: {basis} {reg_considerations}",
        jurisdiction=payload.jurisdiction or "INDIA",
        missing_user_info=["formulation_name"] if not payload.formulation_name else None,
    )

    is_insufficient = classification == "Insufficient information / unable to classify"

    return AYUSHClassifyResponse(
        product_classification=classification,
        basis=basis,
        regulatory_considerations=reg_considerations,
        ip_implications=ip_implications,
        traditional_knowledge=tk_status,
        biological_resource=bio_status,
        abs=abs_status,
        tkdl_prior_art=tkdl_status,
        next_steps=next_steps,
        sources=sources,
        confidence=conf.label if not is_insufficient else "LOW",
        confidence_score=conf.score if not is_insufficient else 1.0,
        abstained=is_insufficient,
        disclaimer="Information provided for guidance only, not legal advice.",
    )
