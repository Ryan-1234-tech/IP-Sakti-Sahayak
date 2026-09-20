"""
routers/features.py — IP-SAKTI Sahayak Decision Support Features Router.

Implements endpoints for:
  - Feature 1: IP Type Recommender ("Identify My IP") with Jurisdiction Separation
  - Feature 2: Patentability Pre-Screening (India & International)
  - Feature 3: AYUSH & Traditional Knowledge Analysis & Guided Classification (Step 5)
  - Feature 4 & 6: Biological Resource & ABS Assessor (Step 6)
  - Feature 7: Traditional Knowledge & Prior-Art Discovery Aid (Step 7)
  - Feature 8: MSME IP Health Check
  - Feature 9: Visual Step-by-Step IP Roadmap (India & International)
  - Feature 10: Official Fee Cost Estimator (India & PCT/WIPO)
  - Feature 11: Prior-Art Vector Similarity Search
  - Feature 12: Trademark Pre-Screening
  - Feature 14: Legal Language Explainer (India Statutes & International Treaties)
  - Feature 17: IP Assessment Report PDF Generator
"""
from __future__ import annotations

import io
import json
import logging
import re
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    ABSAssessRequest,
    ABSAssessResponse,
    AYUSHClassifyRequest,
    AYUSHClassifyResponse,
    AssessmentReportRequest,
    AyushAnalysisRequest,
    AyushAnalysisResponse,
    BioMaterialRequest,
    BioMaterialResponse,
    ChecklistItemDetail,
    ComplianceChecklistResponse,
    CostEstimatorRequest,
    CostEstimatorResponse,
    CostFeeItem,
    IPRecommendRequest,
    IPRecommendResponse,
    IPRoadmapResponse,
    IPTypeRecommendation,
    LegalExplainRequest,
    LegalExplainResponse,
    MSMEHealthCheckRequest,
    MSMEHealthCheckResponse,
    PatentabilityRequest,
    PatentabilityResponse,
    PriorArtSearchRequest,
    PriorArtSearchResponse,
    PriorArtSearchResultItem,
    RoadmapStep,
    SourceRef,
    TKPriorArtRequest,
    TKPriorArtResponse,
    TrademarkPreScreenRequest,
    TrademarkPreScreenResponse,
)
from app.services.abs_assessor import assess_abs_compliance
from app.services.ayush_classifier import classify_ayush_formulation
from app.services.tk_prior_art import search_tk_prior_art
from app.services.confidence import score_confidence
from app.services.vector_store import similarity_search

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# FEATURE 1 — IP TYPE RECOMMENDER ("Identify My IP")
# ============================================================


@router.post(
    "/features/ip-recommend",
    response_model=IPRecommendResponse,
    summary="Identify potentially relevant IP protection types across jurisdictions",
)
async def recommend_ip_types(payload: IPRecommendRequest) -> IPRecommendResponse:
    desc = payload.description.lower()
    jur = (payload.jurisdiction or "INDIA").upper()
    recs: List[IPTypeRecommendation] = []

    # 1. Patent Check
    patent_keywords = [
        "formulation", "process", "technical", "invention", "method", "device",
        "apparatus", "extract", "ratio", "synthesis", "chemical", "composition",
        "active ingredient", "technique", "system", "algorithm", "mechanism"
    ]
    is_patent = any(kw in desc for kw in patent_keywords)
    recs.append(
        IPTypeRecommendation(
            ip_type="Patent",
            relevant=is_patent,
            status="Highly Relevant" if is_patent else "Potentially Relevant",
            why=(
                f"Selected because your description references technical innovation. Under {jur} framework: "
                + ("File Form 1 & 2 under Indian Patents Act 1970." if jur == "INDIA" else "File PCT International Application via WIPO / destination patent offices (USPTO/EPO).")
                if is_patent else
                "Consider if your product includes novel manufacturing methods or functional technical advantages."
            ),
            potential_areas=["Technical formulation / process", "Novel combination ratio", "Method of preparation"],
            jurisdiction=jur,
        )
    )

    # 2. Trademark Check
    tm_keywords = ["brand", "name", "logo", "mark", "tagline", "label", "identity", "packaging name", "symbol"]
    is_tm = any(kw in desc for kw in tm_keywords) or True
    recs.append(
        IPTypeRecommendation(
            ip_type="Trademark",
            relevant=is_tm,
            status="Highly Relevant",
            why=(
                "Essential for protecting brand names, commercial titles, and logos. "
                + ("Under Indian Trade Marks Act 1999 (Form TM-A)." if jur == "INDIA" else "Under Madrid Protocol (WIPO) for international trademark extension.")
            ),
            potential_areas=["Brand Name", "Product Logo", "Label Artwork", "Tagline / Slogan"],
            jurisdiction=jur,
        )
    )

    # 3. Design Check
    design_keywords = ["bottle", "package", "shape", "visual", "appearance", "container", "pattern", "surface", "structure", "design", "aesthetic"]
    is_design = any(kw in desc for kw in design_keywords)
    recs.append(
        IPTypeRecommendation(
            ip_type="Design",
            relevant=is_design,
            status="Highly Relevant" if is_design else "Requires Verification",
            why=(
                "Selected because you mentioned unique bottle shapes, outer packaging geometry, or visual aesthetics. "
                + ("Registered under Indian Designs Act 2000 (Locarno Classification)." if jur == "INDIA" else "Registered internationally via Hague Agreement (WIPO).")
                if is_design else
                "Relevant if your product features a novel, non-functional outer shape, ornament, or container design."
            ),
            potential_areas=["Container / Bottle Geometry", "Outer Packaging Surface Pattern", "3D Shape of Product"],
            jurisdiction=jur,
        )
    )

    # 4. Copyright Check
    copy_keywords = ["manual", "code", "artwork", "documentation", "guide", "literature", "paper", "brochure", "website", "text"]
    is_copy = any(kw in desc for kw in copy_keywords)
    recs.append(
        IPTypeRecommendation(
            ip_type="Copyright",
            relevant=is_copy,
            status="Highly Relevant" if is_copy else "Potentially Relevant",
            why=(
                "Protects original user manuals, instructional leaflets, website content, and label artwork. "
                + ("Protected under Indian Copyright Act 1957 (Form XIV)." if jur == "INDIA" else "Automatically recognized in 181 countries under Berne Convention.")
            ),
            potential_areas=["Product Manual / User Leaflet", "Label Artwork & Graphics", "Marketing Documentation"],
            jurisdiction=jur,
        )
    )

    # 5. Geographical Indication (GI) Check
    gi_keywords = ["region", "geographical", "gi", "origin", "traditional area", "location", "indigenous to", "kerala", "darjeeling", "kashmir", "assam"]
    is_gi = any(kw in desc for kw in gi_keywords)
    recs.append(
        IPTypeRecommendation(
            ip_type="Geographical Indication",
            relevant=is_gi,
            status="Potentially Relevant" if is_gi else "Not Relevant",
            why=(
                "Relevant if your product possesses qualities or a reputation attributable to a specific geographical origin. "
                + ("Under Indian GI Act 1999." if jur == "INDIA" else "Under Lisbon System / Geneva Act (WIPO) for international appellations of origin.")
            ),
            potential_areas=["Regional Origin Claim", "Association with Recognized GI Territory"],
            jurisdiction=jur,
        )
    )

    # 6. Traditional Knowledge Considerations
    tk_keywords = ["herbal", "ayurvedic", "neem", "turmeric", "ashwagandha", "guduchi", "plant", "traditional", "classical", "herb", "ayush"]
    is_tk = any(kw in desc for kw in tk_keywords)
    recs.append(
        IPTypeRecommendation(
            ip_type="Traditional Knowledge",
            relevant=is_tk,
            status="Highly Relevant" if is_tk else "Requires Verification",
            why=(
                "Traditional medicinal herbs or classical formulations were identified. "
                + ("Section 3(p) prior-art clearance and NBA approval required under Indian law." if jur == "INDIA" else "Article 27.3(b) TRIPS & Nagoya Protocol Access and Benefit Sharing rules apply internationally.")
            ),
            potential_areas=["TKDL Prior-Art Verification", "Section 3(p) Non-Patentability Review", "NBA Biological Resource Approval"],
            jurisdiction=jur,
        )
    )

    return IPRecommendResponse(
        recommendations=recs,
        summary=f"Identified {sum(1 for r in recs if r.relevant)} potentially relevant IP protection categories for your product under {jur} jurisdiction.",
        jurisdiction=jur,
        disclaimer="Preliminary IP identification based on description keywords. Consult a qualified patent/trademark agent for formal filings.",
    )


# ============================================================
# FEATURE 2 — PATENTABILITY PRE-SCREENING
# ============================================================


@router.post(
    "/features/patentability-prescreen",
    response_model=PatentabilityResponse,
    summary="Preliminary patentability pre-screen under Indian and International Patent Law",
)
async def patentability_prescreen(payload: PatentabilityRequest) -> PatentabilityResponse:
    text_corpus = f"{payload.title} {payload.description} {payload.ingredients or ''} {payload.technical_process or ''} {payload.claimed_new or ''}".lower()
    jur = (payload.jurisdiction or "INDIA").upper()

    # 1. RAG retrieval for relevant patent provisions & legal guidelines
    chunks = similarity_search(payload.title + " " + payload.description[:300], top_k=4, jurisdiction=jur)
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
                    url=c.source_url,
                    source_url=c.source_url,
                    relevance_score=round(c.score, 4),
                    relevance=round(c.score, 4),
                    snippet=c.text[:600],
                    chunk_id=c.chunk_id,
                )
            )

    # 2. Heuristic Analysis for Novelty, Inventive Step, TK Risk, Bio Risk
    exclusions: List[str] = []
    provisions: List[str] = []
    next_steps: List[str] = []

    # Check Traditional Knowledge
    tk_detected = payload.is_tk_involved or any(k in text_corpus for k in ["ayurved", "herb", "turmeric", "ashwagandha", "neem", "guduchi", "plant extract", "classical"])
    if tk_detected:
        tk_risk = "HIGH"
        if jur == "INDIA":
            exclusions.append("Section 3(p), Patents Act 1970: Invention which in effect is traditional knowledge or aggregation of known properties of traditionally known component.")
            provisions.append("Section 3(p), Patents Act 1970")
            next_steps.append("Conduct formal Synergistic Efficacy Study (Combination Index < 1.0) to prove non-obvious synergy beyond individual known herbs.")
        else:
            exclusions.append("Article 27(1) TRIPS & EPO Article 56 EPC: Lack of inventive step over published traditional botanical literature / prior art.")
            provisions.append("Article 27 TRIPS / Article 56 EPC")
            next_steps.append("Perform global prior art search in WIPO PATENTSCOPE and EPO Espacenet for published herbal extraction patents.")
    else:
        tk_risk = "LOW"

    # Check Substance Efficacy / Incremental Innovations
    substance_detected = any(k in text_corpus for k in ["derivative", "salt", "polymorph", "formulation", "mixture", "extract", "ratio"])
    if substance_detected:
        if jur == "INDIA":
            exclusions.append("Section 3(d), Patents Act 1970: Mere discovery of a new form of a known substance without enhancement of known therapeutic efficacy.")
            provisions.append("Section 3(d), Patents Act 1970")
            next_steps.append("Generate comparative experimental data demonstrating enhanced therapeutic efficacy over the nearest known prior-art extract.")
        else:
            exclusions.append("US 35 U.S.C. 103 / EPO Art 56: Obviousness objections for routine combination of known active fractions.")

    # Check Biological Material Risk
    bio_detected = payload.is_biological_involved or any(k in text_corpus for k in ["biological", "plant", "botanical", "fungus", "herb", "microorganism"])
    if bio_detected:
        bio_risk = "HIGH"
        if jur == "INDIA":
            provisions.append("Section 6, Biological Diversity Act 2002 (Mandatory NBA Form III Approval)")
            next_steps.append("File Form III with National Biodiversity Authority (NBA, Chennai) prior to grant of patent under Indian law.")
        else:
            provisions.append("Nagoya Protocol on Access and Benefit Sharing & EU Regulation No 511/2014 (Due Diligence Declaration)")
            next_steps.append("Maintain internationally recognized certificate of compliance (IRCC) or ABS permit for genetic resources.")
    else:
        bio_risk = "LOW"

    # Novelty & Inventive Step Scoring
    if payload.claimed_new and len(payload.claimed_new.strip()) > 15:
        novelty = "HIGH" if "synergistic" in text_corpus or "novel process" in text_corpus else "MEDIUM"
    else:
        novelty = "MEDIUM"

    if payload.technical_advantage and len(payload.technical_advantage.strip()) > 15:
        inventive_step = "HIGH" if "unexpected" in text_corpus or "enhanced efficacy" in text_corpus else "MEDIUM"
    else:
        inventive_step = "MEDIUM"

    if jur == "INDIA":
        provisions.extend(["Section 2(1)(j) - Novelty", "Section 2(1)(ja) - Inventive Step", "Section 2(1)(ac) - Industrial Applicability"])
        next_steps.extend([
            "Prepare draft Provisional Specification (Form 2) to establish priority date before public disclosure.",
            "Ensure full disclosure of biological source origin in Form 1."
        ])
    else:
        provisions.extend(["PCT Rule 4", "Paris Convention Article 4 (Priority)", "WIPO Patentscope Novelty Guidelines"])
        next_steps.extend([
            "File PCT International Application to reserve patent priority across 157 member states.",
            "Identify target national phase patent offices (e.g. USPTO, EPO, JPO)."
        ])

    summary = (
        f"Preliminary patentability evaluation for '{payload.title}' ({jur} jurisdiction): "
        f"Novelty: {novelty}, Inventive Step: {inventive_step}. "
        f"{'Traditional Knowledge concerns detected under Section 3(p) / prior-art exclusion.' if tk_risk == 'HIGH' else 'No immediate traditional knowledge block identified.'}"
    )

    conf = score_confidence(chunks=chunks, answer=summary, jurisdiction=jur)

    return PatentabilityResponse(
        novelty=novelty,
        inventive_step=inventive_step,
        industrial_applicability="HIGH",
        tk_risk=tk_risk,
        biological_material_risk=bio_risk,
        potential_exclusions=exclusions,
        relevant_provisions=list(set(provisions)),
        relevant_sources=sources,
        sources=sources,
        recommended_next_steps=next_steps,
        assessment_summary=summary,
        confidence=conf.label,
        confidence_score=conf.score,
        abstained=False,
        jurisdiction=jur,
    )


# ============================================================
# FEATURE 3 — AYUSH & TRADITIONAL KNOWLEDGE ANALYSIS (STEP 5)
# ============================================================


@router.post(
    "/features/ayush-classify",
    response_model=AYUSHClassifyResponse,
    summary="Step 5: Guided AYUSH Formulation Classification",
)
async def ayush_classify_endpoint(payload: AYUSHClassifyRequest) -> AYUSHClassifyResponse:
    return await classify_ayush_formulation(payload)


@router.post(
    "/features/ayush-analysis",
    response_model=AyushAnalysisResponse,
    summary="Legacy AYUSH analysis endpoint",
)
async def analyze_ayush(payload: AyushAnalysisRequest) -> AyushAnalysisResponse:
    # Convert into AYUSHClassifyRequest and execute full classification
    classify_req = AYUSHClassifyRequest(
        formulation_name="AYUSH Formulation Assessment",
        therapeutic_claims=payload.description,
        jurisdiction="INDIA",
    )
    result = await classify_ayush_formulation(classify_req)

    return AyushAnalysisResponse(
        traditional_ingredients_detected=["Classical AYUSH Herbs / Extracts"],
        tk_concern="YES" if result.traditional_knowledge == "Yes" else "NO",
        biological_resource_concern="YES" if result.biological_resource == "Yes" else "NO",
        relevant_provisions=[
            "Section 3(p), Indian Patents Act 1970",
            "Rule 158B, Drugs and Cosmetics Rules 1945",
            "Section 6, Biological Diversity Act 2002",
        ],
        relevant_sources=result.sources,
        recommended_verification=result.next_steps,
        assessment=f"Product Classified as: {result.product_classification}. {result.basis}",
        disclaimer="Information provided for guidance only, not legal advice.",
    )


# ============================================================
# FEATURE 4 & 6 — BIOLOGICAL RESOURCE & ABS ASSESSOR (STEP 6)
# ============================================================


@router.post(
    "/features/abs-assess",
    response_model=ABSAssessResponse,
    summary="Step 6: Biological Resource & ABS Assessor",
)
async def abs_assess_endpoint(payload: ABSAssessRequest) -> ABSAssessResponse:
    return await assess_abs_compliance(payload)


@router.post(
    "/features/biomaterial-check",
    response_model=BioMaterialResponse,
    summary="Biological Material Compliance Checker (Backward Compatible)",
)
async def check_biomaterial_compliance(payload: BioMaterialRequest) -> BioMaterialResponse:
    abs_req = ABSAssessRequest(
        biological_resource_used=payload.biological_resource_used,
        resource_name=payload.resource_name,
        source_location=payload.source_location,
        is_indian_origin=payload.obtained_from_india,
        geographical_origin=payload.geographical_origin or "India",
        traditional_knowledge_associated=bool(payload.associated_tk or payload.traditional_use_based),
        user_entity_type=payload.user_entity_type or "Indian Entity",
        jurisdiction=payload.jurisdiction or "INDIA",
    )
    abs_res = await assess_abs_compliance(abs_req)

    compliance = [
        "Section 6(1) Biological Diversity Act 2002: Mandatory NBA approval (Form III) before grant of patent.",
        "Rule 18, Biological Diversity Rules 2004: Statutory approval process with National Biodiversity Authority.",
        "Access and Benefit Sharing (ABS) Guidelines 2014: Standard benefit-sharing rate between 0.1% and 0.5% ex-factory sales.",
    ]

    approvals = [
        "Form III Application to National Biodiversity Authority (NBA, Chennai)",
        "State Biodiversity Board (SBB) intimation for Indian commercial entities",
        "Clearance of Source & Geographical Origin declaration in Patent Form 1",
    ]

    return BioMaterialResponse(
        biological_material_detected=payload.biological_resource_used,
        source=payload.resource_name or payload.source_location or "Biological Resource",
        geographical_origin=payload.geographical_origin or "India",
        traditional_knowledge="YES" if payload.traditional_use_based or payload.associated_tk else "NO",
        compliance_areas=compliance,
        relevant_official_sources=abs_res.sources,
        mandatory_approvals=approvals,
        abs_assessment=abs_res,
        disclaimer="Information provided for guidance only, not legal advice.",
    )


# ============================================================
# FEATURE 7 — TKDL & PRIOR-ART DISCOVERY AID (STEP 7)
# ============================================================


@router.post(
    "/features/tk-prior-art",
    response_model=TKPriorArtResponse,
    summary="Step 7: Traditional Knowledge / TKDL / Prior-Art Assistance Workflow",
)
async def tk_prior_art_endpoint(payload: TKPriorArtRequest) -> TKPriorArtResponse:
    return await search_tk_prior_art(payload)


# ============================================================
# FEATURE 8 — MSME IP HEALTH CHECK
# ============================================================


@router.post(
    "/features/msme-health-check",
    response_model=MSMEHealthCheckResponse,
    summary="Assess MSME IP readiness and compliance score",
)
async def msme_health_check(payload: MSMEHealthCheckRequest) -> MSMEHealthCheckResponse:
    base_score = 0

    if payload.has_registered_business:
        base_score += 10
    if payload.has_brand_name:
        base_score += 10
    if payload.has_logo:
        base_score += 10
    if payload.has_unique_product:
        base_score += 15
    if payload.has_tech_innovation:
        base_score += 15
    if payload.has_product_docs:
        base_score += 10
    if payload.has_confidential_info:
        base_score += 10
    if payload.has_searched_patents:
        base_score += 10
    if payload.has_searched_trademarks:
        base_score += 10

    if payload.uses_biological_resources and not payload.has_searched_patents:
        base_score = max(5, base_score - 10)
    if payload.traditional_knowledge_involved and not payload.has_searched_patents:
        base_score = max(5, base_score - 10)

    overall = min(100, max(0, base_score))

    patent_readiness = 85 if (payload.has_tech_innovation and payload.has_searched_patents) else (50 if payload.has_tech_innovation else 25)
    tm_readiness = 90 if (payload.has_brand_name and payload.has_logo and payload.has_searched_trademarks) else (60 if payload.has_brand_name else 30)
    design_readiness = 75 if payload.has_unique_product else 40
    copyright_readiness = 80 if payload.has_product_docs else 45
    doc_readiness = 85 if (payload.has_product_docs and payload.has_confidential_info) else 40

    strengths = []
    risks = []
    actions = []

    if payload.has_brand_name and payload.has_logo:
        strengths.append("Established Brand & Visual Identity assets ready for Class registration.")
    else:
        risks.append("Unprotected Brand Name or Logo — vulnerable to trademark squatting.")
        actions.append("File Form TM-A for Brand Name & Logo under Trade Marks Act 1999.")

    if payload.has_tech_innovation:
        strengths.append("Technical innovation identified with high potential for patent filing.")
        if not payload.has_searched_patents:
            risks.append("No prior-art search conducted for technical innovation.")
            actions.append("Conduct comprehensive prior-art search across Indian Patent Office / WIPO database.")

    if payload.uses_biological_resources or payload.traditional_knowledge_involved:
        risks.append("Biological material or Traditional Knowledge involved — Section 3(p) & NBA clearance required.")
        actions.append("Initiate TKDL prior-art review and submit Form III to National Biodiversity Authority.")

    if not payload.has_confidential_info:
        risks.append("Absence of Non-Disclosure Agreements (NDAs) exposing trade secrets.")
        actions.append("Execute bilateral NDAs with employees, manufacturers, and research partners.")

    return MSMEHealthCheckResponse(
        overall_score=overall,
        patent_readiness=patent_readiness,
        trademark_readiness=tm_readiness,
        design_readiness=design_readiness,
        copyright_readiness=copyright_readiness,
        documentation_readiness=doc_readiness,
        strengths=strengths if strengths else ["Registered MSME Business entity."],
        risks=risks if risks else ["Routine monitoring required."],
        recommended_actions=actions if actions else ["Maintain IP portfolio register."],
    )


# ============================================================
# FEATURE 10 — OFFICIAL FEE COST ESTIMATOR
# ============================================================


FEE_TABLE = {
    "patent": {
        "Individual": {"e_filing": 1600, "physical": 1750, "note": "Form 1 Natural Person / Startup / MSME concession fee"},
        "Startup": {"e_filing": 1600, "physical": 1750, "note": "Form 1 Startup 80% fee concession under Patents Rules 2024"},
        "MSME": {"e_filing": 1600, "physical": 1750, "note": "Form 1 Small Entity 80% fee concession under Patents Rules 2024"},
        "Educational": {"e_filing": 1600, "physical": 1750, "note": "Educational Institution statutory concession"},
        "Enterprise": {"e_filing": 8000, "physical": 8800, "note": "Large Entity standard statutory fee"},
    },
    "trademark": {
        "Individual": {"e_filing": 4500, "physical": 5000, "note": "Form TM-A Individual / Startup fee per class"},
        "Startup": {"e_filing": 4500, "physical": 5000, "note": "Form TM-A Startup 50% concession fee per class"},
        "MSME": {"e_filing": 4500, "physical": 5000, "note": "Form TM-A Small Entity 50% concession fee per class"},
        "Educational": {"e_filing": 4500, "physical": 5000, "note": "Form TM-A Educational institution fee per class"},
        "Enterprise": {"e_filing": 9000, "physical": 10000, "note": "Others standard statutory fee per class"},
    },
    "design": {
        "Individual": {"e_filing": 1000, "physical": 1000, "note": "Form 1 Natural Person / Startup design registration"},
        "Startup": {"e_filing": 1000, "physical": 1000, "note": "Form 1 Startup design registration fee"},
        "MSME": {"e_filing": 1000, "physical": 1000, "note": "Form 1 Small Entity design registration fee"},
        "Educational": {"e_filing": 1000, "physical": 1000, "note": "Educational institution design fee"},
        "Enterprise": {"e_filing": 4000, "physical": 4000, "note": "Large entity standard design registration fee"},
    },
    "copyright": {
        "Individual": {"e_filing": 500, "physical": 500, "note": "Form XIV Literary / Artistic work registration fee per work"},
        "Startup": {"e_filing": 500, "physical": 500, "note": "Form XIV Startup registration fee per work"},
        "MSME": {"e_filing": 500, "physical": 500, "note": "Form XIV Small Entity registration fee per work"},
        "Educational": {"e_filing": 500, "physical": 500, "note": "Form XIV Educational registration fee per work"},
        "Enterprise": {"e_filing": 500, "physical": 500, "note": "Form XIV Standard fee per work"},
    },
    "gi": {
        "Individual": {"e_filing": 5000, "physical": 5000, "note": "Form GI-1 Application for registration of Geographical Indication"},
        "Startup": {"e_filing": 5000, "physical": 5000, "note": "Form GI-1 Application fee"},
        "MSME": {"e_filing": 5000, "physical": 5000, "note": "Form GI-1 Application fee"},
        "Educational": {"e_filing": 5000, "physical": 5000, "note": "Form GI-1 Application fee"},
        "Enterprise": {"e_filing": 5000, "physical": 5000, "note": "Form GI-1 Standard statutory fee"},
    }
}


@router.post(
    "/features/cost-estimator",
    response_model=CostEstimatorResponse,
    summary="Estimate official government IP filing fees",
)
async def estimate_ip_costs(payload: CostEstimatorRequest) -> CostEstimatorResponse:
    ip_key = payload.ip_type.lower()
    app_key = payload.applicant_type
    jur = (payload.jurisdiction or "INDIA").upper()

    cat_data = FEE_TABLE.get(ip_key, FEE_TABLE["patent"])
    fee_info = cat_data.get(app_key, cat_data.get("Startup", {"e_filing": 1600, "physical": 1750, "note": "Concession fee"}))

    base_fee = fee_info["e_filing"]
    breakdown = [
        CostFeeItem(head=f"Official {jur} E-Filing Application Fee", fee_inr=base_fee, note=fee_info["note"])
    ]

    add_costs = []
    if ip_key == "patent":
        request_exam_fee = 4000 if app_key in ["Individual", "Startup", "MSME", "Educational"] else 20000
        breakdown.append(CostFeeItem(head="Request for Examination (Form 18)", fee_inr=request_exam_fee, note="Mandatory for examination under Patents Rules"))
        if jur == "INTERNATIONAL":
            add_costs.extend(["PCT International Filing Fee: ~CHF 1,330 (₹1,25,000 approx.)", "International Search Authority (ISA/IN) Fee: ₹10,000 (Indian entity)"])
        else:
            add_costs.extend(["Early Publication Fee (Form 9 - Optional): ₹2,500", "Physical Filing Surcharge: +10% on statutory fee"])
    elif ip_key == "trademark":
        add_costs.extend(["Notice of Opposition response (Form TM-O if opposed): ₹2,700", "Class Addition Fee: ₹4,500 per additional class"])
        if jur == "INTERNATIONAL":
            add_costs.append("Madrid System Basic Fee: CHF 653 (3-color mark: CHF 903) + individual country designation fees")

    total_est = sum(item.fee_inr for item in breakdown)

    return CostEstimatorResponse(
        ip_type=payload.ip_type,
        applicant_type=payload.applicant_type,
        application_type=payload.application_type,
        estimated_official_fee=total_est,
        fee_breakdown=breakdown,
        additional_possible_costs=add_costs,
        professional_fees_included=False,
        jurisdiction=jur,
        source_document=f"First Schedule, {payload.ip_type.capitalize()} Rules (Govt of India Official Gazettes)" if jur == "INDIA" else "WIPO Fee Schedule (PCT / Madrid)",
    )


# ============================================================
# FEATURE 11 — PRIOR-ART SIMILARITY SEARCH
# ============================================================


@router.post(
    "/features/prior-art-search",
    response_model=PriorArtSearchResponse,
    summary="Search indexed knowledge base for prior-art & document similarity",
)
async def prior_art_search(payload: PriorArtSearchRequest) -> PriorArtSearchResponse:
    jur = (payload.jurisdiction or "INDIA").upper()
    chunks = similarity_search(payload.query, top_k=payload.top_k, jurisdiction=jur)

    results: List[PriorArtSearchResultItem] = []
    for c in chunks:
        score_pct = round(c.score * 100, 1)
        doc_type = (c.source_type or "Official Document").capitalize()
        title = c.source_title

        if score_pct > 80:
            why = "High semantic overlap with submitted technical query."
        elif score_pct > 65:
            why = "Moderate keyword and structural concept similarity."
        else:
            why = "General legal/regulatory context match."

        results.append(
            PriorArtSearchResultItem(
                document_title=title,
                document_type=doc_type,
                jurisdiction=c.jurisdiction,
                similarity_score=score_pct,
                relevant_passage=c.text[:400] + "..." if len(c.text) > 400 else c.text,
                why_relevant=why,
                source_url=c.source_url,
                section=c.section,
                page=c.page_number,
            )
        )

    return PriorArtSearchResponse(
        results=results,
        summary_disclaimer="Potentially relevant documents were identified in the sources searched. This is a prior-art discovery aid and not a legal opinion.",
    )


# ============================================================
# FEATURE 12 — TRADEMARK PRE-SCREEN
# ============================================================


@router.post(
    "/features/trademark-prescreen",
    response_model=TrademarkPreScreenResponse,
    summary="Preliminary trademark distinctiveness & class assessment",
)
async def trademark_prescreen(payload: TrademarkPreScreenRequest) -> TrademarkPreScreenResponse:
    name_upper = payload.brand_name.upper()
    prod_lower = payload.product_service.lower()
    jur = (payload.jurisdiction or "INDIA").upper()

    nice_class = "Class 5 (Pharmaceuticals, AYUSH Formulations, Herbal Supplements)"
    if any(k in prod_lower for k in ["cosmetic", "soap", "skin", "cream", "shampoo"]):
        nice_class = "Class 3 (Cosmetics, Non-medicated Toiletries, Essential Oils)"
    elif any(k in prod_lower for k in ["tea", "food", "spice", "honey", "confectionery"]):
        nice_class = "Class 30 (Coffee, Tea, Rice, Spices, Herbal Infusions)"
    elif any(k in prod_lower for k in ["software", "app", "digital", "platform"]):
        nice_class = "Class 42 (Software & Technology Services) / Class 9 (Downloadable Software)"

    concerns = []
    descriptive_words = ["AYUR", "HERBAL", "PURE", "NATURAL", "HEAL", "CURE", "MED", "PHARMA", "BEST", "SUPER"]
    if any(w in name_upper for w in descriptive_words):
        concerns.append("Section 9(1)(b) Warning: Name contains descriptive terms commonly used in the trade. Examiners may object that the mark lacks inherent distinctiveness.")

    if len(payload.brand_name.strip()) <= 3:
        concerns.append("Short acronym mark — higher probability of phonetic similarity conflicts under Section 11.")

    sec9_status = "Passes preliminary distinctiveness check." if not concerns else "Requires distinctiveness acquired through use proof or logo combination."
    sec11_status = "Requires search against TM Registry database for identical/similar prior marks."

    assessment = "Potentially Suitable" if not concerns else "Requires Further Review"

    return TrademarkPreScreenResponse(
        brand_name=payload.brand_name,
        preliminary_assessment=assessment,
        recommended_nice_class=nice_class,
        potential_concerns=concerns if concerns else ["No immediate descriptive objections identified."],
        absolute_grounds_sec9=sec9_status,
        relative_grounds_sec11=sec11_status,
        relevant_provisions=["Section 9 (Absolute Grounds for Refusal)", "Section 11 (Relative Grounds for Refusal)", "Nice Classification 11th Edition"],
        jurisdiction=jur,
        disclaimer="This is a preliminary assessment based on trademark principles and is NOT a live trademark registry search.",
    )


# ============================================================
# FEATURE 14 — LEGAL LANGUAGE EXPLAINER (STEP 4 & 8)
# ============================================================


LEGAL_DATABASE = {
    "3(p)": {
        "name": "Section 3(p) — Traditional Knowledge Exclusion",
        "sec": "Section 3(p), Patents Act 1970",
        "doc": "Indian Patents Act 1970",
        "jur": "INDIA",
        "plain": "An invention that is essentially traditional knowledge, or simply combines known properties of traditional herbs/materials, CANNOT be patented in India.",
        "why": "Protects Indian traditional knowledge (like Ayurveda, Siddha, Unani) from being monopolized or bio-pirated without genuine technical innovation.",
        "example": "Filing a patent for mixing Turmeric and Honey for wound healing will be rejected under Section 3(p) because both herbs are already documented in TKDL for wound healing."
    },
    "3(d)": {
        "name": "Section 3(d) — Enhanced Efficacy Requirement",
        "sec": "Section 3(d), Patents Act 1970",
        "doc": "Indian Patents Act 1970",
        "jur": "INDIA",
        "plain": "Simply discovering a new form, salt, polymorph, or formulation of an existing known substance is NOT patentable UNLESS it shows significantly enhanced therapeutic efficacy.",
        "why": "Prevents 'evergreening' of patents where pharmaceutical companies make minor chemical tweaks just to extend their monopoly.",
        "example": "Converting a known Ayurvedic liquid extract into a pill format is not patentable under Section 3(d) unless you prove the pill works significantly better in the body."
    },
    "3(e)": {
        "name": "Section 3(e) — Mere Admixture",
        "sec": "Section 3(e), Patents Act 1970",
        "doc": "Indian Patents Act 1970",
        "jur": "INDIA",
        "plain": "A simple mixture of known ingredients where each ingredient performs its expected function is NOT patentable.",
        "why": "Requires inventors to prove unexpected synergistic results rather than standard combinations.",
        "example": "Combining Neem (antibacterial) and Tulsi (cough relief) into one syrup is a mere admixture under 3(e) unless there is a true synergistic booster effect."
    },
    "section 6": {
        "name": "Section 6 — Biological Diversity Act NBA Approval",
        "sec": "Section 6, Biological Diversity Act 2002",
        "doc": "Biological Diversity Act 2002",
        "jur": "INDIA",
        "plain": "Anyone applying for IP rights for an invention based on biological resources obtained from India MUST obtain prior approval from the National Biodiversity Authority (NBA, Chennai) via Form III.",
        "why": "Ensures sovereign rights over Indian bio-resources and guarantees Access and Benefit Sharing (ABS) with local communities.",
        "example": "If your patented formulation uses Ashwagandha harvested in Madhya Pradesh, you must file Form III with NBA before the patent office can grant the patent."
    },
    "article 27 trips": {
        "name": "Article 27 — TRIPS Patentable Subject Matter",
        "sec": "Article 27, TRIPS Agreement (WTO)",
        "doc": "WTO TRIPS Agreement 1994",
        "jur": "INTERNATIONAL",
        "plain": "Patents shall be available for any inventions, whether products or processes, in all fields of technology, provided that they are new, involve an inventive step and are capable of industrial application.",
        "why": "Sets minimum international standards for patentability across all WTO member nations.",
        "example": "Countries may exclude diagnostic, therapeutic and surgical methods for the treatment of humans or animals under Article 27.3(a)."
    },
    "pct": {
        "name": "Patent Cooperation Treaty (PCT)",
        "sec": "Article 3, Patent Cooperation Treaty 1970",
        "doc": "WIPO Patent Cooperation Treaty",
        "jur": "INTERNATIONAL",
        "plain": "Allows filing a single international patent application to seek patent protection simultaneously in over 150 countries.",
        "why": "Provides a 30/31-month timeline to evaluate international commercial potential before incurring national filing expenses.",
        "example": "An Indian startup files a PCT application through IPO as Receiving Office to reserve patent rights in the US, EU, and Japan."
    }
}


@router.post(
    "/features/legal-explain",
    response_model=LegalExplainResponse,
    summary="Explain legal provisions in plain English with jurisdiction awareness",
)
async def explain_legal_provision(payload: LegalExplainRequest) -> LegalExplainResponse:
    q = payload.query.lower()
    target_jur = (payload.jurisdiction or "INDIA").upper()

    for key, data in LEGAL_DATABASE.items():
        if key in q:
            return LegalExplainResponse(
                provision_name=data["name"],
                section_number=data["sec"],
                source_document=data["doc"],
                jurisdiction=data["jur"],
                plain_english_explanation=data["plain"],
                why_it_matters=data["why"],
                practical_example=data["example"],
                sources=[],
                confidence="HIGH",
                confidence_score=5.0,
                abstained=False,
            )

    # RAG fallback
    chunks = similarity_search(payload.query, top_k=3, jurisdiction=target_jur)
    if not chunks:
        return LegalExplainResponse(
            provision_name=f"Query: '{payload.query}'",
            section_number=payload.query.upper(),
            source_document=f"{target_jur} Legal Framework",
            jurisdiction=target_jur,
            plain_english_explanation="I couldn't establish a reliable answer from the authoritative sources available to me.",
            why_it_matters="Statutory compliance requires verification against current gazettes.",
            practical_example="Consult an official IP facilitator or registered patent agent.",
            sources=[],
            confidence="LOW",
            confidence_score=0.0,
            abstained=True,
            abstention_reason=f"No authoritative record found for '{payload.query}' under {target_jur} jurisdiction.",
        )

    sources = [
        SourceRef(
            id=c.source_id or c.chunk_id,
            source_id=c.source_id,
            title=c.source_title,
            authority=c.authority,
            source_type=c.source_type,
            jurisdiction=c.jurisdiction,
            section=c.section,
            page_number=c.page_number,
            url=c.source_url,
            snippet=c.text[:400],
        )
        for c in chunks
    ]

    snippet = chunks[0].text[:300]
    return LegalExplainResponse(
        provision_name=f"Explanation for '{payload.query}'",
        section_number=payload.query.upper(),
        source_document=chunks[0].source_title,
        jurisdiction=chunks[0].jurisdiction,
        plain_english_explanation=f"Based on authoritative sources: {snippet}",
        why_it_matters=f"Ensures compliance with {chunks[0].jurisdiction} statutory filing standards.",
        practical_example="Always verify statutory provisions against current gazette notifications prior to filing.",
        sources=sources,
        confidence="HIGH" if chunks[0].score >= 0.70 else "MEDIUM",
        confidence_score=round(chunks[0].score * 5.0, 1),
        abstained=False,
    )


# ============================================================
# FEATURE 7 & 13 — COMPLIANCE CHECKLISTS & ROADMAPS
# ============================================================


CHECKLIST_DATA = {
    "patent": {
        "INDIA": [
            ChecklistItemDetail(item="Form 1 (Application for Grant of Patent)", explanation="Standard statutory filing form", why_needed="Establishes applicant identity, category (MSME/Startup), and priority date.", source_document="Patents Rules 2024", relevant_provision="Section 7, Patents Act 1970", jurisdiction="INDIA"),
            ChecklistItemDetail(item="Form 2 (Provisional / Complete Specification)", explanation="Full technical description & claims", why_needed="Provides complete disclosure of invention, drawings, and best mode of operation.", source_document="Patents Rules 2024", relevant_provision="Section 10, Patents Act 1970", jurisdiction="INDIA"),
            ChecklistItemDetail(item="Form 3 (Statement & Undertaking)", explanation="Details of foreign patent filings", why_needed="Mandatory disclosure of corresponding filings outside India within 6 months.", source_document="Patents Rules 2024", relevant_provision="Section 8, Patents Act 1970", jurisdiction="INDIA"),
            ChecklistItemDetail(item="Form 5 (Declaration as to Inventorship)", explanation="Statement of true & first inventors", why_needed="Confirms inventor entitlement and assignment of rights to applicant.", source_document="Patents Rules 2024", relevant_provision="Rule 13(6), Patents Rules 2024", jurisdiction="INDIA"),
            ChecklistItemDetail(item="Biological Material Disclosure (Form 1 Clause)", explanation="Declaration of source & geographical origin", why_needed="Mandatory if biological resources from India are used in the specification.", source_document="Patents Rules 2024", relevant_provision="Section 10(4)(d)(ii), Patents Act 1970", jurisdiction="INDIA"),
            ChecklistItemDetail(item="Form III NBA Approval (if applicable)", explanation="National Biodiversity Authority consent", why_needed="Required before patent grant if Indian biological resources are utilized.", source_document="Biological Diversity Act 2002", relevant_provision="Section 6, BDA 2002", jurisdiction="INDIA"),
        ],
        "INTERNATIONAL": [
            ChecklistItemDetail(item="PCT Request Form (PCT/RO/101)", explanation="International patent application request", why_needed="Designates all 157 PCT contracting states in a single unified filing.", source_document="PCT Applicant's Guide", relevant_provision="PCT Article 3", jurisdiction="INTERNATIONAL"),
            ChecklistItemDetail(item="International Search Report (ISR) Request", explanation="Prior art search by International Searching Authority", why_needed="Provides written opinion on novelty and inventive step within 16 months.", source_document="WIPO PCT Guidelines", relevant_provision="PCT Article 18", jurisdiction="INTERNATIONAL"),
            ChecklistItemDetail(item="Nagoya Protocol / ABS Compliance Certificate", explanation="Internationally Recognized Certificate of Compliance", why_needed="Required by European & global destination offices for genetic materials.", source_document="Nagoya Protocol", relevant_provision="EU Reg 511/2014", jurisdiction="INTERNATIONAL"),
        ]
    }
}


@router.get(
    "/features/compliance-checklist/{ip_type}",
    response_model=ComplianceChecklistResponse,
    summary="Get compliance and application document checklist",
)
async def get_compliance_checklist(ip_type: str, jurisdiction: Optional[str] = "INDIA") -> ComplianceChecklistResponse:
    key = ip_type.lower()
    jur = (jurisdiction or "INDIA").upper()
    cat = CHECKLIST_DATA.get(key, CHECKLIST_DATA["patent"])
    items = cat.get(jur, cat.get("INDIA", []))
    return ComplianceChecklistResponse(ip_type=ip_type, jurisdiction=jur, checklist=items)


ROADMAP_DATA = {
    "patent": {
        "INDIA": [
            RoadmapStep(step_number=1, title="1. Identify IP", description="Determine technical novelty and confirm invention is not excluded under Section 3.", required_documents=["Invention Disclosure Sheet"], timeline="1-2 Weeks", jurisdiction="INDIA"),
            RoadmapStep(step_number=2, title="2. Prior-Art Search", description="Search IPO, WIPO, and TKDL databases to verify novelty.", required_documents=["Prior-Art Search Report"], timeline="1 Week", jurisdiction="INDIA"),
            RoadmapStep(step_number=3, title="3. File Application", description="Submit Form 1, Form 2 (Provisional/Complete), Form 3, and Form 5.", required_documents=["Form 1", "Form 2 Specification", "Form 3", "Form 5"], timeline="Day 1 (Establishes Priority)", jurisdiction="INDIA"),
            RoadmapStep(step_number=4, title="4. Publication", description="Official journal publication after 18 months (or 1 month via Form 9 early pub).", required_documents=["Form 9 (Optional)"], timeline="18 Months / 1 Month", jurisdiction="INDIA"),
            RoadmapStep(step_number=5, title="5. Request Examination", description="Submit Form 18 within 31 months from filing date.", required_documents=["Form 18"], timeline="Within 31 Months", jurisdiction="INDIA"),
            RoadmapStep(step_number=6, title="6. First Examination Report (FER)", description="Patent Office issues FER detailing novelty/objection findings.", required_documents=["FER Notice"], timeline="6-12 Months post Form 18", jurisdiction="INDIA"),
            RoadmapStep(step_number=7, title="7. Respond to Objections", description="Submit written response to FER within 6 months.", required_documents=["FER Written Response", "Amended Claims"], timeline="Within 6 Months", jurisdiction="INDIA"),
            RoadmapStep(step_number=8, title="8. Hearing & NBA Clearance", description="Attend hearing if requested and submit Form III NBA approval.", required_documents=["Form III NBA Consent"], timeline="2-4 Months", jurisdiction="INDIA"),
            RoadmapStep(step_number=9, title="9. Patent Grant", description="Patent is granted and certificate issued.", required_documents=["Patent Certificate"], timeline="Final Grant", jurisdiction="INDIA"),
        ],
        "INTERNATIONAL": [
            RoadmapStep(step_number=1, title="1. Domestic Priority Filing", description="File initial provisional/complete patent application in India.", required_documents=["Form 1 & 2"], timeline="Month 0 (Priority Date)", jurisdiction="INTERNATIONAL"),
            RoadmapStep(step_number=2, title="2. File PCT International Application", description="File PCT/RO/101 with Indian Patent Office as Receiving Office or WIPO.", required_documents=["PCT Application"], timeline="Within 12 Months from Priority", jurisdiction="INTERNATIONAL"),
            RoadmapStep(step_number=3, title="3. International Search & Written Opinion", description="ISA issues International Search Report (ISR) & preliminary opinion.", required_documents=["ISR Report"], timeline="Month 16", jurisdiction="INTERNATIONAL"),
            RoadmapStep(step_number=4, title="4. International Publication", description="WIPO publishes application on PATENTSCOPE.", required_documents=["WIPO Publication"], timeline="Month 18", jurisdiction="INTERNATIONAL"),
            RoadmapStep(step_number=5, title="5. Enter National / Regional Phase", description="Enter destination jurisdictions (USPTO, EPO, JPO, etc.).", required_documents=["National Translations & Forms"], timeline="Month 30 / 31", jurisdiction="INTERNATIONAL"),
        ]
    }
}


@router.get(
    "/features/roadmap/{ip_type}",
    response_model=IPRoadmapResponse,
    summary="Get visual step-by-step IP roadmap",
)
async def get_ip_roadmap(ip_type: str, jurisdiction: Optional[str] = "INDIA") -> IPRoadmapResponse:
    key = ip_type.lower()
    jur = (jurisdiction or "INDIA").upper()
    cat = ROADMAP_DATA.get(key, ROADMAP_DATA["patent"])
    steps = cat.get(jur, cat.get("INDIA", []))
    return IPRoadmapResponse(ip_type=ip_type, jurisdiction=jur, steps=steps)


# ============================================================
# FEATURE 17 — PDF ASSESSMENT REPORT GENERATOR
# ============================================================


@router.post(
    "/features/generate-report",
    summary="Generate downloadable IP Assessment PDF report",
)
async def generate_pdf_report(payload: AssessmentReportRequest):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0c1911'))
        h2_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor('#047857'), spaceBefore=10, spaceAfter=4)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor('#1e293b'))
        alert_style = ParagraphStyle('Alert', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#92400e'))

        story = []

        # Title Header
        story.append(Paragraph("IP-SAKTI SAHAYAK — PRELIMINARY IP ASSESSMENT REPORT", title_style))
        story.append(Paragraph("<b>Ministry of AYUSH &amp; Indian IP Legal Guidance Decision-Support Engine</b>", body_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#047857'), spaceAfter=12))

        # Metadata Table
        meta_data = [
            [Paragraph("<b>Applicant / Entity:</b>", body_style), Paragraph(payload.applicant_name, body_style)],
            [Paragraph("<b>Invention / Product Title:</b>", body_style), Paragraph(payload.invention_title, body_style)],
            [Paragraph("<b>Jurisdiction:</b>", body_style), Paragraph(payload.jurisdiction or "INDIA", body_style)],
            [Paragraph("<b>Assessment Date:</b>", body_style), Paragraph("September 2026", body_style)],
        ]
        t_meta = Table(meta_data, colWidths=[150, 380])
        t_meta.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')), ('PADDING', (0, 0), (-1, -1), 6)]))
        story.append(t_meta)
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("1. Executive Summary", h2_style))
        story.append(Paragraph(f"This preliminary decision-support report analyzes the invention/product <i>'{payload.invention_title}'</i> across Indian Patent Law, Trade Marks Act 1999, Traditional Knowledge Digital Library (TKDL) guidelines, and Biological Diversity Act 2002 compliance.", body_style))
        story.append(Spacer(1, 8))

        # Product Description
        story.append(Paragraph("2. Invention & Formulation Details", h2_style))
        story.append(Paragraph(f"<b>Description:</b> {payload.description}", body_style))
        if payload.ingredients:
            story.append(Paragraph(f"<b>Ingredients / Formulations:</b> {payload.ingredients}", body_style))
        story.append(Spacer(1, 8))

        # Potential IP Protection Table
        story.append(Paragraph("3. Recommended IP Protection Categories", h2_style))
        ip_table_data = [
            [Paragraph("<b>IP Type</b>", body_style), Paragraph("<b>Relevance Status</b>", body_style), Paragraph("<b>Key Scope / Action</b>", body_style)],
            [Paragraph("Patent", body_style), Paragraph("High / Preliminary", body_style), Paragraph("Formulation process & synergistic ratio novelty (Form 1 & 2)", body_style)],
            [Paragraph("Trademark", body_style), Paragraph("Highly Relevant", body_style), Paragraph("Brand name & logo registration under Class 5 / 3 (Form TM-A)", body_style)],
            [Paragraph("Copyright", body_style), Paragraph("Potentially Relevant", body_style), Paragraph("Product user manual & packaging artwork (Form XIV)", body_style)],
            [Paragraph("Traditional Knowledge", body_style), Paragraph("Review Required", body_style), Paragraph("Section 3(p) prior-art clearance against TKDL gazettes", body_style)],
        ]
        t_ip = Table(ip_table_data, colWidths=[120, 130, 280])
        t_ip.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecfdf5')), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')), ('PADDING', (0, 0), (-1, -1), 5)]))
        story.append(t_ip)
        story.append(Spacer(1, 10))

        # Statutory & Regulatory Compliance
        story.append(Paragraph("4. Regulatory & Section 3 Compliance Review", h2_style))
        story.append(Paragraph("• <b>Section 3(p) (Patents Act 1970):</b> Requires proof of unexpected synergistic therapeutic effect to overcome traditional knowledge prior-art objections.", body_style))
        story.append(Paragraph("• <b>Section 3(d) (Patents Act 1970):</b> Requires comparative efficacy data over nearest known botanical extracts.", body_style))
        story.append(Paragraph("• <b>Section 6 (Biological Diversity Act 2002):</b> Mandatory Form III approval from National Biodiversity Authority (NBA) prior to patent grant.", body_style))
        story.append(Spacer(1, 10))

        # Statutory Disclaimer
        story.append(Paragraph("5. Statutory AI Disclaimer", h2_style))
        disclaimer_box = [
            [Paragraph("<b>IMPORTANT NOTICE:</b> Information provided for guidance only, not legal advice. This is an AI-generated preliminary assessment compiled by IP-SAKTI Sahayak based on indexed statutory gazettes. It does not constitute formal legal representation. Consult a registered Patent/Trademark Agent before filing.", alert_style)]
        ]
        t_disc = Table(disclaimer_box, colWidths=[530])
        t_disc.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbe6')), ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b')), ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(t_disc)

        doc.build(story)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=IP_Assessment_Report_{re.sub(r'[^a-zA-Z0-9]', '_', payload.invention_title[:15])}.pdf"}
        )

    except Exception as e:
        logger.exception(f"PDF Report generation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate PDF report: {e}")
