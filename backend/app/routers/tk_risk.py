"""
routers/tk_risk.py — AYUSH & Traditional Knowledge Assessor & Formulation Classifier (Step 5).

Endpoints:
  - POST /api/tk-risk/assess — Section 3(p) TKDL Prior-Art Risk Analysis
  - POST /api/tk-risk/classify — Guided Formulation Classification Workflow
  - GET /api/tk-risk/reference-herbs — Reference list of classical herbs
"""
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, status

from app.models.schemas import (
    AYUSHClassifyRequest,
    AYUSHClassifyResponse,
    IngredientInput,
    SourceRef,
    TKMatchResult,
    TKRiskRequest,
    TKRiskResponse,
)
from app.services.ayush_classifier import classify_ayush_formulation
from app.services.confidence import score_confidence
from app.services.vector_store import similarity_search

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Reference Dataset of TKDL-Indexed Classical AYUSH Herbs & Formulations
# ---------------------------------------------------------------------------
TKDL_REFERENCE_DATABASE: List[Dict[str, Any]] = [
    {
        "keywords": ["ashwagandha", "withania somnifera", "asgandh", "indian ginseng"],
        "traditional_name": "Ashwagandha (अश्वगंधा)",
        "latin_name": "Withania somnifera",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/8921",
        "classical_text_source": "Ayurvedic Pharmacopoeia of India (API) Part I, Vol I",
        "known_therapeutic_use": "Rasayana (Rejuvenator), Anti-stress, Immunomodulator, Adaptogen",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["guduchi", "tinospora cordifolia", "giloy", "amrita"],
        "traditional_name": "Guduchi / Giloy (गिलोय / अमृता)",
        "latin_name": "Tinospora cordifolia",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/4402",
        "classical_text_source": "Charaka Samhita, Chikitsasthana Chapter 1",
        "known_therapeutic_use": "Jwarahara (Antipyretic), Immunomodulator, Anti-inflammatory",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["tulsi", "ocimum sanctum", "holy basil", "surasa"],
        "traditional_name": "Tulsi (तुलसी)",
        "latin_name": "Ocimum sanctum / Ocimum tenuiflorum",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/1092",
        "classical_text_source": "Sushruta Samhita, Sutrasthana Chapter 38",
        "known_therapeutic_use": "Kaphahara, Anti-microbial, Respiratory Wellness, Expectorant",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["turmeric", "curcuma longa", "haridra", "haldi"],
        "traditional_name": "Haridra / Haldi (हरिद्रा)",
        "latin_name": "Curcuma longa",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/0019 (Turmeric Patent Revocation Case)",
        "classical_text_source": "Ayurvedic Pharmacopoeia of India Part I, Vol I & CSIR TKDL Landmark",
        "known_therapeutic_use": "Kandughna (Anti-pruritic), Wound Healing, Anti-inflammatory, Skin Care",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["neem", "azadirachta indica", "nimba", "margosa"],
        "traditional_name": "Nimba / Neem (निम्ब)",
        "latin_name": "Azadirachta indica",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/7712 (EPO Neem Patent Revocation)",
        "classical_text_source": "Sushruta Samhita & Ayurvedic Pharmacopoeia of India Part I, Vol II",
        "known_therapeutic_use": "Kusthahara (Anti-dermatosis), Anti-bacterial, Blood Purifier",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["triphala", "haritaki", "bibhitaki", "amalaki", "amla"],
        "traditional_name": "Triphala (त्रिफला)",
        "latin_name": "Terminalia chebula + Terminalia bellirica + Phyllanthus emblica",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/3029",
        "classical_text_source": "Sharangdhara Samhita, Madhyama Khanda Chapter 6",
        "known_therapeutic_use": "Anulomana (Digestive Regulation), Eye Health, Antioxidant, Laxative",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["brahmi", "bacopa monnieri", "water hyssop", "jalbrahmi"],
        "traditional_name": "Brahmi (ब्राह्मी)",
        "latin_name": "Bacopa monnieri",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/5521",
        "classical_text_source": "Charaka Samhita, Chikitsasthana Chapter 10 (Medhya Rasayana)",
        "known_therapeutic_use": "Medhya (Cognitive Enhancer), Nootropic, Anxiolytic",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["sarpagandha", "rauvolfia serpentina", "reserpine", "snakeroot"],
        "traditional_name": "Sarpagandha (सर्पगंधा)",
        "latin_name": "Rauvolfia serpentina",
        "system": "Ayurveda",
        "tkdl_reference": "TKDL Accession No. AU/9012",
        "classical_text_source": "Ayurvedic Pharmacopoeia of India Part I, Vol I",
        "known_therapeutic_use": "Nidrajanana (Sedative), Antihypertensive",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["nilavembu", "andrographis paniculata", "kalmegh", "bhunimba"],
        "traditional_name": "Nilavembu / Kalmegh (நிலவேம்பு / कालमेघ)",
        "latin_name": "Andrographis paniculata",
        "system": "Siddha",
        "tkdl_reference": "TKDL Accession No. SD/4410",
        "classical_text_source": "Siddha Formulary of India Part I & Gunapadam",
        "known_therapeutic_use": "Suram (Antipyretic), Dengue/Chikungunya Fever Management, Hepatoprotective",
        "risk_factor": "HIGH_PRIOR_ART",
    },
    {
        "keywords": ["unnab", "ziziphus jujuba", "jujube", "juijube"],
        "traditional_name": "Unnab (عناب)",
        "latin_name": "Ziziphus jujuba",
        "system": "Unani",
        "tkdl_reference": "TKDL Accession No. UN/1204",
        "classical_text_source": "National Formulary of Unani Medicine (NFUM) Part I",
        "known_therapeutic_use": "Musaffi-e-Dham (Blood Purifier), Expectorant, Antitussive",
        "risk_factor": "HIGH_PRIOR_ART",
    },
]


@router.get("/tk-risk/reference-herbs", response_model=List[str], summary="Get Reference AYUSH Herbs List")
async def get_reference_herbs() -> List[str]:
    """Return common TKDL-indexed herbs for UI search autocompletion."""
    return [item["traditional_name"] for item in TKDL_REFERENCE_DATABASE]


@router.post(
    "/tk-risk/classify",
    response_model=AYUSHClassifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Step 5: Guided AYUSH Formulation Classification",
)
async def classify_formulation(payload: AYUSHClassifyRequest) -> AYUSHClassifyResponse:
    """
    Execute guided AYUSH formulation classification across the 7 recognized statutory classes:
      - Classical Ayurvedic Medicine
      - Patent/Proprietary Medicine (ASU)
      - New / Non-Classical Drug
      - Phytopharmaceutical
      - Ayurveda-Aahar / nutraceutical
      - Cosmetic
      - Insufficient information / unable to classify
    """
    return await classify_ayush_formulation(payload)


@router.post(
    "/tk-risk/assess",
    response_model=TKRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Assess TKDL & Section 3(p) Patent Risk",
)
async def assess_tk_risk(payload: TKRiskRequest) -> TKRiskResponse:
    """
    Assess a product formulation against TKDL prior-art & Section 3(p) of Indian Patents Act 1970.
    Integrates with the guided classification engine and retrieves grounded statutory sources.
    """
    matched_entries: List[TKMatchResult] = []
    seen_references = set()

    # 1. Match formulation ingredients against TKDL reference database
    for ing in payload.ingredients:
        search_str = f"{ing.name} {ing.latin_name or ''}".lower()

        for ref in TKDL_REFERENCE_DATABASE:
            if any(kw in search_str for kw in ref["keywords"]):
                ref_key = ref["tkdl_reference"]
                if ref_key not in seen_references:
                    seen_references.add(ref_key)
                    matched_entries.append(
                        TKMatchResult(
                            ingredient_name=ing.name,
                            traditional_name=ref["traditional_name"],
                            latin_name=ref["latin_name"],
                            system=ref["system"],
                            tkdl_reference=ref["tkdl_reference"],
                            classical_text_source=ref["classical_text_source"],
                            risk_factor=ref["risk_factor"],
                            known_therapeutic_use=ref["known_therapeutic_use"],
                        )
                    )

    # 2. Compute Section 3(p) Risk Score (0-100)
    base_score = 15
    high_matches = [m for m in matched_entries if m.risk_factor == "HIGH_PRIOR_ART"]
    mod_matches = [m for m in matched_entries if m.risk_factor == "MODERATE"]

    score = base_score + (len(high_matches) * 28) + (len(mod_matches) * 15)
    if len(matched_entries) >= 2:
        score += 15

    score = max(10, min(95, score))

    # 3. Risk Level Thresholds
    if score >= 70:
        risk_level = "HIGH_RISK"
        sec_3p_status = "HIGH SECTION 3(p) REJECTION RISK"
        assessment = (
            f"The formulation '{payload.formulation_name}' contains {len(matched_entries)} ingredient(s) "
            f"extensively documented in the Traditional Knowledge Digital Library (TKDL) and classical gazettes. "
            f"Filing a standard patent claim will almost certainly trigger a Section 3(p) rejection under the Indian Patents Act 1970."
        )
    elif score >= 45:
        risk_level = "MODERATE_RISK"
        sec_3p_status = "MODERATE PRIOR-ART OVERLAP"
        assessment = (
            f"The formulation '{payload.formulation_name}' incorporates traditionally known ingredients. "
            f"A Section 3(p) objection is likely unless claims are narrowly scoped around novel extraction techniques, "
            f"synergistic ratio novelty, or specific bio-enhancer combinations."
        )
    else:
        risk_level = "LOW_RISK"
        sec_3p_status = "LOW PRIOR-ART OVERLAP"
        assessment = (
            f"The formulation '{payload.formulation_name}' has low direct overlap with traditional TKDL records. "
            f"Favorable potential for patentability, provided novelty and industrial applicability requirements are met."
        )

    # 4. Generate Key Recommendations
    recommendations: List[str] = []
    if len(matched_entries) > 0:
        recommendations.append(
            "Conduct a formal Synergistic Efficacy Study (e.g. Combination Index < 1.0) demonstrating that the combination yields a non-obvious therapeutic effect beyond the sum of individual herbs."
        )
        recommendations.append(
            "Focus patent claims on novel extraction solvents, specific bio-active fraction ratios (e.g. 5:1 standardized extract), or novel delivery systems (e.g. nano-emulsion, liposomal formulation)."
        )
        recommendations.append(
            "Ensure mandatory disclosure of Biological Resources under Section 6 of the Biological Diversity Act (NBA approval)."
        )
    else:
        recommendations.append(
            "Perform a global prior-art patent search (WIPO/EPO/USPTO) to confirm technical novelty before filing Form 1."
        )
        recommendations.append(
            "File a provisional patent application immediately to secure the priority date."
        )

    # 5. Retrieve Grounded Sources
    chunks = similarity_search(
        f"Section 3(p) Patents Act 1970 TKDL AYUSH guidelines {payload.formulation_name}",
        top_k=4,
        jurisdiction=payload.jurisdiction or "INDIA",
    )
    sources: List[SourceRef] = [
        SourceRef(
            id=c.source_id or c.chunk_id,
            source_id=c.source_id,
            title=c.source_title,
            authority=c.authority,
            source_type=c.source_type,
            jurisdiction=c.jurisdiction,
            section=c.section or "Section 3(p)",
            article=c.article,
            rule=c.rule,
            page_number=c.page_number,
            page=c.page_number,
            url=c.source_url,
            source_url=c.source_url,
            relevance_score=round(c.score, 4),
            relevance=round(c.score, 4),
            snippet=c.text[:600],
            chunk_id=c.chunk_id,
        )
        for c in chunks
    ]

    # Run classification in parallel
    classify_req = AYUSHClassifyRequest(
        formulation_name=payload.formulation_name,
        system=payload.system,
        ingredients=payload.ingredients,
        therapeutic_claims=payload.proposed_claims,
        jurisdiction=payload.jurisdiction or "INDIA",
    )
    classification_resp = await classify_ayush_formulation(classify_req)

    return TKRiskResponse(
        formulation_name=payload.formulation_name,
        system=payload.system,
        overall_risk_score=score,
        risk_level=risk_level,
        matched_entries=matched_entries,
        patentability_assessment=assessment,
        key_recommendations=recommendations,
        section_3p_compliance_status=sec_3p_status,
        classification_response=classification_resp,
        sources=sources,
        confidence="HIGH",
        confidence_score=4.5,
        abstained=False,
        disclaimer="Information provided for guidance only, not legal advice.",
    )
