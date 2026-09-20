"""
models/schemas.py — Pydantic request/response models for all API endpoints.
Includes full citation metadata, jurisdiction separation, AYUSH classification,
ABS assessor, TKDL prior-art discovery, and confidence/safe abstention.
"""
from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field


# ============================================================
# Shared sub-models & Source-Cited Provenance
# ============================================================


class SourceRef(BaseModel):
    """A single retrieved knowledge-base source cited in an answer with full legal metadata."""

    id: str = Field(description="Unique source or chunk ID")
    source_id: Optional[str] = None
    title: str
    authority: Optional[str] = None
    source_type: Optional[str] = None  # act | rule | guideline | manual | treaty | circular
    document_type: Optional[str] = None
    jurisdiction: str = Field(default="INDIA", description="INDIA | INTERNATIONAL")
    section: Optional[str] = None
    article: Optional[str] = None
    rule: Optional[str] = None
    page_number: Optional[int] = None
    page: Optional[int] = None
    document_version: Optional[str] = None
    effective_date: Optional[str] = None
    url: Optional[str] = None
    source_url: Optional[str] = None
    relevance_score: Optional[float] = None
    relevance: Optional[float] = None
    snippet: Optional[str] = None
    chunk_id: Optional[str] = None


class Action(BaseModel):
    """A next-step action generated from the answer."""

    step: int
    description: str
    required_documents: List[str] = Field(default_factory=list)


class DeadlineInfo(BaseModel):
    deadline_date: Optional[str] = None
    description: Optional[str] = None


class DocumentSummary(BaseModel):
    doc_type: str = ""
    summary: str = ""
    deadline_date: Optional[str] = None
    key_requirements: List[str] = Field(default_factory=list)


# ============================================================
# POST /api/chat
# ============================================================


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4096, description="User's question")
    language: Optional[str] = Field(None, description="BCP-47 language tag, e.g. 'hi', 'ta'")
    conversation_id: Optional[str] = Field(None, description="Resume an existing conversation")
    jurisdiction: Optional[str] = Field(default="INDIA", description="INDIA | INTERNATIONAL")


class ChatResponse(BaseModel):
    message_id: str
    conversation_id: str
    answer: str
    sources: List[SourceRef] = Field(default_factory=list)
    citations: List[SourceRef] = Field(default_factory=list)
    confidence: str = Field(description="HIGH | MEDIUM | LOW")
    confidence_score: float
    abstained: bool = False
    abstention_reason: Optional[str] = None
    human_facilitator_available: bool = True
    actions: List[Action] = Field(default_factory=list)
    detected_language: Optional[str] = None
    jurisdiction: str = "INDIA"


# ============================================================
# POST /api/upload
# ============================================================


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    extracted_text_preview: str = Field(description="First ~500 chars of extracted text")
    page_count: int = 0


# ============================================================
# POST /api/document/analyze
# ============================================================


class DocumentAnalyzeRequest(BaseModel):
    document_id: str
    question: Optional[str] = None
    language: Optional[str] = None
    jurisdiction: Optional[str] = "INDIA"


class DocumentAnalyzeResponse(BaseModel):
    document_id: str
    summary: DocumentSummary
    deadline: Optional[DeadlineInfo] = None
    requirements: List[str] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    confidence: str = "MEDIUM"
    confidence_score: float = 0.0
    abstained: bool = False
    answer: Optional[str] = None


# ============================================================
# GET /api/sources
# ============================================================


class SourceListItem(BaseModel):
    id: str
    title: str
    authority: Optional[str] = None
    url: Optional[str] = None
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = "INDIA"
    topic: Optional[str] = None
    publication_date: Optional[str] = None


class SourcesResponse(BaseModel):
    sources: List[SourceListItem]
    total: int


# ============================================================
# POST /api/feedback
# ============================================================


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(..., description="1 for thumbs-up, -1 for thumbs-down")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    ok: bool
    message_id: str


# ============================================================
# Generic error
# ============================================================


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    extra: Optional[Any] = None


# ============================================================
# Business Profile & Compliance Passport Schemas
# ============================================================


class IPAssetSchema(BaseModel):
    asset_type: str = Field(description="Patent | Trademark | GI | Copyright | Traditional Knowledge")
    title: str = Field(..., min_length=1)
    status: str = Field(default="Granted", description="Granted | Pending | Draft | Expired")
    registration_no: Optional[str] = None


class BusinessProfileCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=256)
    sector: str = Field(default="AYUSH", description="AYUSH | Pharma | Biotech | Software | MSME | Other")
    company_type: str = Field(default="Startup", description="Startup | MSME | Enterprise | Researcher")
    registration_number: Optional[str] = None
    state: Optional[str] = None
    ip_assets: List[IPAssetSchema] = Field(default_factory=list)


class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    sector: Optional[str] = None
    company_type: Optional[str] = None
    registration_number: Optional[str] = None
    state: Optional[str] = None
    ip_assets: Optional[List[IPAssetSchema]] = None


class BusinessProfileResponse(BaseModel):
    id: str
    company_name: str
    sector: str
    company_type: str
    registration_number: Optional[str] = None
    state: Optional[str] = None
    ip_assets: List[IPAssetSchema] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ChecklistItem(BaseModel):
    item: str
    status: str = Field(description="PASSED | WARNING | CRITICAL")
    guidance: str


class AssetBreakdown(BaseModel):
    patents_count: int = 0
    trademarks_count: int = 0
    copyrights_count: int = 0
    gis_count: int = 0
    total_assets: int = 0


class CompliancePassportResponse(BaseModel):
    profile_id: str
    company_name: str
    sector: str
    company_type: str
    overall_score: int = Field(description="Compliance Score between 0 and 100")
    status_level: str = Field(description="EXCELLENT | GOOD | NEEDS_ATTENTION | HIGH_RISK")
    asset_breakdown: AssetBreakdown
    compliance_checklist: List[ChecklistItem] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    next_filing_deadline: Optional[str] = None


# ============================================================
# Step 5: Guided AYUSH Formulation Classification Schemas
# ============================================================


class IngredientInput(BaseModel):
    name: str = Field(..., min_length=1, description="Common or traditional herb name e.g. Ashwagandha")
    latin_name: Optional[str] = Field(None, description="Botanical name e.g. Withania somnifera")
    percentage: Optional[float] = Field(None, description="Composition percentage")
    is_novel: bool = False
    is_biological: bool = True


class AYUSHClassifyRequest(BaseModel):
    formulation_name: str = Field(..., min_length=1, max_length=256)
    formulation_source: Optional[str] = Field(
        None,
        description="Classical Text (First Schedule) | In-house R&D | Modified Classical | Modern Extract",
    )
    authoritative_classical_text: Optional[str] = Field(
        None,
        description="e.g. Charaka Samhita, Sushruta Samhita, Ayurvedic Pharmacopoeia of India (API), AFI, NFUM",
    )
    ingredients: List[IngredientInput] = Field(default_factory=list)
    novel_ingredients: Optional[List[str]] = Field(default_factory=list)
    biological_materials_used: bool = True
    intended_use: Optional[str] = Field(
        None,
        description="Therapeutic / Disease cure | Health maintenance / dietary | Topical cosmetic | Rejuvenation (Rasayana)",
    )
    therapeutic_claims: Optional[str] = None
    product_type: str = Field(
        default="Oral Internal",
        description="Oral Internal | Topical Cream/Oil | Tablet/Capsule | Liquid Decoction | Food/Beverage | Cosmetic",
    )
    commercialization_intent: bool = True
    system: str = Field(default="Ayurveda", description="Ayurveda | Siddha | Unani | Polyherbal")
    jurisdiction: Optional[str] = "INDIA"


class AYUSHClassifyResponse(BaseModel):
    product_classification: str = Field(
        description="Classical Ayurvedic Medicine | Patent/Proprietary Medicine | New / Non-Classical Drug | Phytopharmaceutical | Ayurveda-Aahar / nutraceutical | Cosmetic | Insufficient information / unable to classify"
    )
    basis: str
    regulatory_considerations: str
    ip_implications: str
    traditional_knowledge: str = Field(description="Yes | No | Uncertain")
    biological_resource: str = Field(description="Yes | No | Uncertain")
    abs: str = Field(description="Review indicated | Not indicated | Uncertain")
    tkdl_prior_art: str = Field(description="Recommended | Not indicated")
    next_steps: List[str] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    confidence: str = Field(description="HIGH | MEDIUM | LOW")
    confidence_score: float = 0.0
    abstained: bool = False
    disclaimer: str = "Information provided for guidance only, not legal advice."


# Legacy TK-Risk schema for backward compatibility
class TKRiskRequest(BaseModel):
    formulation_name: str = Field(..., min_length=1, max_length=256)
    system: str = Field(default="Ayurveda", description="Ayurveda | Siddha | Unani | Polyherbal")
    ingredients: List[IngredientInput] = Field(..., min_items=1)
    proposed_claims: Optional[str] = None
    jurisdiction: Optional[str] = "INDIA"


class TKMatchResult(BaseModel):
    ingredient_name: str
    traditional_name: str
    latin_name: str
    system: str
    tkdl_reference: str
    classical_text_source: str
    risk_factor: str = Field(description="HIGH_PRIOR_ART | MODERATE | LOW")
    known_therapeutic_use: str


class TKRiskResponse(BaseModel):
    formulation_name: str
    system: str
    overall_risk_score: int = Field(description="Section 3(p) Patent Rejection Risk (0-100)")
    risk_level: str = Field(description="HIGH_RISK | MODERATE_RISK | LOW_RISK")
    matched_entries: List[TKMatchResult] = Field(default_factory=list)
    patentability_assessment: str
    key_recommendations: List[str] = Field(default_factory=list)
    section_3p_compliance_status: str
    classification_response: Optional[AYUSHClassifyResponse] = None
    sources: List[SourceRef] = Field(default_factory=list)
    confidence: str = "HIGH"
    confidence_score: float = 4.0
    abstained: bool = False
    disclaimer: str = "Information provided for guidance only, not legal advice."


# ============================================================
# Step 6: Biological Resource & ABS Assessor Schemas
# ============================================================


class ABSAssessRequest(BaseModel):
    biological_resource_used: bool = True
    resource_name: Optional[str] = None
    resource_type: Optional[str] = Field(
        None, description="Botanical plant | Microbial | Animal extract | Fungal | Marine"
    )
    source_location: Optional[str] = None
    is_indian_origin: bool = True
    geographical_origin: Optional[str] = "India"
    traditional_knowledge_associated: bool = False
    associated_tk_details: Optional[str] = None
    intended_use: str = Field(
        default="Commercial utilization",
        description="Research | Commercial utilization | Bio-survey / Bio-utilization | Applying for IPR inside India | Applying for IPR outside India",
    )
    commercialization_intent: bool = True
    user_entity_type: str = Field(
        default="Indian Entity",
        description="Indian Entity (no foreign participation) | Non-Indian / Foreign Entity | NRI | Indian Entity with foreign shareholding",
    )
    jurisdiction: Optional[str] = "INDIA"


class ABSAssessResponse(BaseModel):
    biological_resource: str
    traditional_knowledge: str = Field(description="Yes | No | Uncertain")
    abs_review: str
    relevant_framework: str
    next_steps: List[str] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    confidence: str = Field(description="HIGH | MEDIUM | LOW")
    confidence_score: float = 0.0
    abstained: bool = False
    abstention_reason: Optional[str] = None
    disclaimer: str = "Information provided for guidance only, not legal advice."


# Backward compatible alias for biomaterial request
class BioMaterialRequest(BaseModel):
    biological_resource_used: bool = True
    resource_name: Optional[str] = None
    source_location: Optional[str] = None
    geographical_origin: Optional[str] = None
    associated_tk: Optional[str] = None
    obtained_from_india: bool = True
    traditional_use_based: bool = False
    user_entity_type: Optional[str] = "Indian Entity"
    jurisdiction: Optional[str] = "INDIA"


class BioMaterialResponse(BaseModel):
    biological_material_detected: bool
    source: str
    geographical_origin: str
    traditional_knowledge: str
    compliance_areas: List[str] = Field(default_factory=list)
    relevant_official_sources: List[SourceRef] = Field(default_factory=list)
    mandatory_approvals: List[str] = Field(default_factory=list)
    abs_assessment: Optional[ABSAssessResponse] = None
    disclaimer: str = "Information provided for guidance only, not legal advice."


# ============================================================
# Step 7: TKDL + Prior-Art Discovery Schemas
# ============================================================


class TKPriorArtRequest(BaseModel):
    formulation: Optional[str] = None
    ingredients: Optional[str] = None
    traditional_use: Optional[str] = None
    therapeutic_claim: Optional[str] = None
    keywords: Optional[str] = None
    jurisdiction: Optional[str] = "INDIA"


class PriorArtPointer(BaseModel):
    database_name: str
    access_type: str  # Public | Authorized IP Office Access Only | Restricted CSIR Access
    search_url: Optional[str] = None
    recommended_search_strategy: str
    access_note: str


class TKPriorArtResponse(BaseModel):
    traditional_knowledge: str = Field(
        description="Potential indication | No relevant record identified in the sources searched | Unable to determine"
    )
    potential_prior_art: str
    retrieved_evidence: List[SourceRef] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    database_pointers: List[PriorArtPointer] = Field(default_factory=list)
    next_step: str
    confidence: str = "HIGH"
    confidence_score: float = 4.0
    abstained: bool = False
    disclaimer: str = "This is a prior-art discovery aid and not a legal opinion."


# ============================================================
# IP Type Recommender Schemas (Feature 1)
# ============================================================


class IPTypeRecommendation(BaseModel):
    ip_type: str
    relevant: bool
    status: str
    why: str
    potential_areas: List[str] = Field(default_factory=list)
    jurisdiction: str = "INDIA"


class IPRecommendRequest(BaseModel):
    description: str = Field(..., min_length=5, description="Product or invention description")
    jurisdiction: Optional[str] = Field(default="INDIA", description="INDIA | INTERNATIONAL")


class IPRecommendResponse(BaseModel):
    recommendations: List[IPTypeRecommendation]
    summary: str
    jurisdiction: str = "INDIA"
    disclaimer: str = "This is a preliminary assessment and does not constitute legal advice."


# ============================================================
# Patentability Pre-Screen Schemas (Feature 2)
# ============================================================


class PatentabilityRequest(BaseModel):
    title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=10)
    ingredients: Optional[str] = None
    technical_process: Optional[str] = None
    claimed_new: Optional[str] = None
    technical_advantage: Optional[str] = None
    is_tk_involved: bool = False
    is_biological_involved: bool = False
    jurisdiction: Optional[str] = Field(default="INDIA", description="INDIA | INTERNATIONAL")


class PatentabilityResponse(BaseModel):
    novelty: str = "UNKNOWN"
    inventive_step: str = "UNKNOWN"
    industrial_applicability: str = "HIGH"
    tk_risk: str = "UNKNOWN"
    biological_material_risk: str = "UNKNOWN"
    potential_exclusions: List[str] = Field(default_factory=list)
    relevant_provisions: List[str] = Field(default_factory=list)
    relevant_sources: List[SourceRef] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    recommended_next_steps: List[str] = Field(default_factory=list)
    assessment_summary: str
    confidence: str = "HIGH"
    confidence_score: float = 4.0
    abstained: bool = False
    jurisdiction: str = "INDIA"
    disclaimer: str = "Preliminary assessment based on indexed sources. Does not guarantee patentability. Information provided for guidance only, not legal advice."


# ============================================================
# Legal Explainer Schemas (Feature 14)
# ============================================================


class LegalExplainRequest(BaseModel):
    query: str = Field(..., min_length=2, description="e.g. 'Section 3(d)' or 'Article 27 TRIPS'")
    jurisdiction: Optional[str] = Field(default="INDIA", description="INDIA | INTERNATIONAL")


class LegalExplainResponse(BaseModel):
    provision_name: str
    section_number: str
    source_document: str
    jurisdiction: str = "INDIA"
    plain_english_explanation: str
    why_it_matters: str
    practical_example: str
    sources: List[SourceRef] = Field(default_factory=list)
    confidence: str = "HIGH"
    confidence_score: float = 4.0
    abstained: bool = False
    abstention_reason: Optional[str] = None
    disclaimer: str = "Information provided for guidance only, not legal advice."


# ============================================================
# MSME IP Health Check, Cost Estimator, Roadmap Schemas
# ============================================================


class MSMEHealthCheckRequest(BaseModel):
    has_registered_business: bool = False
    has_brand_name: bool = False
    has_logo: bool = False
    has_unique_product: bool = False
    has_tech_innovation: bool = False
    has_product_docs: bool = False
    has_confidential_info: bool = False
    has_searched_patents: bool = False
    has_searched_trademarks: bool = False
    uses_biological_resources: bool = False
    traditional_knowledge_involved: bool = False
    jurisdiction: Optional[str] = "INDIA"


class MSMEHealthCheckResponse(BaseModel):
    overall_score: int
    patent_readiness: int
    trademark_readiness: int
    design_readiness: int
    copyright_readiness: int
    documentation_readiness: int
    strengths: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    disclaimer: str = "Information provided for guidance only, not legal advice."


class CostFeeItem(BaseModel):
    head: str
    fee_inr: int
    note: str


class CostEstimatorRequest(BaseModel):
    ip_type: str = Field(..., description="Patent | Trademark | Design | Copyright | GI")
    applicant_type: str = Field(default="Startup", description="Individual | Startup | MSME | Educational | Enterprise")
    application_type: str = Field(default="Standard", description="Provisional | Complete | Single Class | Multi Class")
    jurisdiction: Optional[str] = "INDIA"


class CostEstimatorResponse(BaseModel):
    ip_type: str
    applicant_type: str
    application_type: str
    estimated_official_fee: int
    fee_breakdown: List[CostFeeItem] = Field(default_factory=list)
    additional_possible_costs: List[str] = Field(default_factory=list)
    professional_fees_included: bool = False
    jurisdiction: str = "INDIA"
    source_document: str = "Official Patent/TM/Copyright/Design Fee Schedules"


class PriorArtSearchRequest(BaseModel):
    query: str = Field(..., min_length=5)
    top_k: int = 5
    jurisdiction: Optional[str] = "INDIA"


class PriorArtSearchResultItem(BaseModel):
    document_title: str
    document_type: str
    jurisdiction: str = "INDIA"
    similarity_score: float
    relevant_passage: str
    why_relevant: str
    source_url: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = None


class PriorArtSearchResponse(BaseModel):
    results: List[PriorArtSearchResultItem] = Field(default_factory=list)
    summary_disclaimer: str = "Potentially relevant documents were identified in the sources searched. This is a prior-art discovery aid and not a legal opinion."


class TrademarkPreScreenRequest(BaseModel):
    brand_name: str = Field(..., min_length=1)
    product_service: str = Field(..., min_length=2)
    industry_category: Optional[str] = None
    jurisdiction: Optional[str] = "INDIA"


class TrademarkPreScreenResponse(BaseModel):
    brand_name: str
    preliminary_assessment: str
    recommended_nice_class: str
    potential_concerns: List[str] = Field(default_factory=list)
    absolute_grounds_sec9: str
    relative_grounds_sec11: str
    relevant_provisions: List[str] = Field(default_factory=list)
    jurisdiction: str = "INDIA"
    disclaimer: str = "This is a preliminary assessment based on trademark principles and is NOT a live trademark availability search."


class ChecklistItemDetail(BaseModel):
    item: str
    explanation: str
    why_needed: str
    source_document: str
    relevant_provision: str
    jurisdiction: str = "INDIA"


class ComplianceChecklistResponse(BaseModel):
    ip_type: str
    jurisdiction: str = "INDIA"
    checklist: List[ChecklistItemDetail] = Field(default_factory=list)


class RoadmapStep(BaseModel):
    step_number: int
    title: str
    description: str
    required_documents: List[str] = Field(default_factory=list)
    timeline: str
    jurisdiction: str = "INDIA"


class IPRoadmapResponse(BaseModel):
    ip_type: str
    jurisdiction: str = "INDIA"
    steps: List[RoadmapStep] = Field(default_factory=list)


class AssessmentReportRequest(BaseModel):
    applicant_name: str = Field(default="Valued Inventor / MSME")
    invention_title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=10)
    ingredients: Optional[str] = None
    brand_name: Optional[str] = None
    product_service: Optional[str] = None
    jurisdiction: Optional[str] = "INDIA"
