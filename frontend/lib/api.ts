/**
 * lib/api.ts — Typed fetch wrappers for all IP-SAKTI Sahayak backend endpoints.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

// ============================================================
// Types
// ============================================================

export interface SourceRef {
  id: string;
  source_id?: string;
  title: string;
  authority?: string;
  source_type?: string;
  document_type?: string;
  jurisdiction?: "INDIA" | "INTERNATIONAL" | string;
  section?: string;
  article?: string;
  rule?: string;
  page_number?: number;
  page?: number;
  document_version?: string;
  effective_date?: string;
  url?: string;
  source_url?: string;
  relevance_score?: number;
  relevance?: number;
  snippet?: string;
  chunk_id?: string;
}

export interface Action {
  step: number;
  description: string;
  required_documents: string[];
}

export interface ChatRequest {
  query: string;
  language?: string;
  conversation_id?: string;
  jurisdiction?: string;
}

export interface ChatResponse {
  message_id: string;
  conversation_id: string;
  answer: string;
  sources: SourceRef[];
  citations?: SourceRef[];
  confidence: "HIGH" | "MEDIUM" | "LOW";
  confidence_score: number;
  abstained?: boolean;
  abstention_reason?: string;
  human_facilitator_available?: boolean;
  actions: Action[];
  detected_language?: string;
  jurisdiction?: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  file_size: number;
  extracted_text_preview: string;
  page_count: number;
}

export interface DocumentSummary {
  doc_type: string;
  summary: string;
  deadline_date?: string;
  key_requirements: string[];
}

export interface DocumentAnalyzeRequest {
  document_id: string;
  question?: string;
  language?: string;
  jurisdiction?: string;
}

export interface DocumentAnalyzeResponse {
  document_id: string;
  summary: DocumentSummary;
  deadline?: { deadline_date?: string; description?: string };
  requirements: string[];
  sources: SourceRef[];
  confidence: string;
  confidence_score: number;
  abstained?: boolean;
  answer?: string;
}

export interface SourceListItem {
  id: string;
  title: string;
  authority?: string;
  url?: string;
  document_type?: string;
  jurisdiction?: string;
  topic?: string;
  publication_date?: string;
}

export interface SourcesResponse {
  sources: SourceListItem[];
  total: number;
}

export interface FeedbackRequest {
  message_id: string;
  rating: 1 | -1;
  comment?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  llm_provider?: string;
  llm_model?: string;
  llm_configured: boolean;
  kb_chunk_count: number;
  message: string;
}

// ============================================================
// Business Profile & Compliance Passport Types
// ============================================================

export interface IPAsset {
  asset_type: "Patent" | "Trademark" | "GI" | "Copyright" | "Traditional Knowledge" | string;
  title: string;
  status: "Granted" | "Pending" | "Draft" | "Expired" | string;
  registration_no?: string;
}

export interface BusinessProfile {
  id?: string;
  company_name: string;
  sector: string;
  company_type: string;
  registration_number?: string;
  state?: string;
  ip_assets: IPAsset[];
  created_at?: string;
  updated_at?: string;
}

export interface ChecklistItem {
  item: string;
  status: "PASSED" | "WARNING" | "CRITICAL";
  guidance: string;
}

export interface CompliancePassport {
  profile_id: string;
  company_name: string;
  sector: string;
  company_type: string;
  overall_score: number;
  status_level: "EXCELLENT" | "GOOD" | "NEEDS_ATTENTION" | "HIGH_RISK";
  asset_breakdown: {
    patents_count: number;
    trademarks_count: number;
    copyrights_count: number;
    gis_count: number;
    total_assets: number;
  };
  compliance_checklist: ChecklistItem[];
  recommended_actions: string[];
  next_filing_deadline?: string;
}

// ============================================================
// Step 5: Guided AYUSH Formulation Classification Types
// ============================================================

export interface IngredientInput {
  name: string;
  latin_name?: string;
  percentage?: number;
  is_novel?: boolean;
  is_biological?: boolean;
}

export interface AYUSHClassifyRequest {
  formulation_name: string;
  formulation_source?: string;
  authoritative_classical_text?: string;
  ingredients: IngredientInput[];
  novel_ingredients?: string[];
  biological_materials_used?: boolean;
  intended_use?: string;
  therapeutic_claims?: string;
  product_type?: string;
  commercialization_intent?: boolean;
  system?: string;
  jurisdiction?: string;
}

export interface AYUSHClassifyResponse {
  product_classification: string;
  basis: string;
  regulatory_considerations: string;
  ip_implications: string;
  traditional_knowledge: "Yes" | "No" | "Uncertain" | string;
  biological_resource: "Yes" | "No" | "Uncertain" | string;
  abs: "Review indicated" | "Not indicated" | "Uncertain" | string;
  tkdl_prior_art: "Recommended" | "Not indicated" | string;
  next_steps: string[];
  sources: SourceRef[];
  confidence: "HIGH" | "MEDIUM" | "LOW" | string;
  confidence_score: number;
  abstained?: boolean;
  disclaimer: string;
}

export interface TKRiskRequest {
  formulation_name: string;
  system: string;
  ingredients: IngredientInput[];
  proposed_claims?: string;
  jurisdiction?: string;
}

export interface TKMatchResult {
  ingredient_name: string;
  traditional_name: string;
  latin_name: string;
  system: string;
  tkdl_reference: string;
  classical_text_source: string;
  risk_factor: "HIGH_PRIOR_ART" | "MODERATE" | "LOW";
  known_therapeutic_use: string;
}

export interface TKRiskResponse {
  formulation_name: string;
  system: string;
  overall_risk_score: number;
  risk_level: "HIGH_RISK" | "MODERATE_RISK" | "LOW_RISK";
  matched_entries: TKMatchResult[];
  patentability_assessment: string;
  key_recommendations: string[];
  section_3p_compliance_status: string;
  classification_response?: AYUSHClassifyResponse;
  sources?: SourceRef[];
  confidence?: string;
  confidence_score?: number;
  abstained?: boolean;
  disclaimer?: string;
}

// ============================================================
// Step 6: Biological Resource & ABS Assessor Types
// ============================================================

export interface ABSAssessRequest {
  biological_resource_used: boolean;
  resource_name?: string;
  resource_type?: string;
  source_location?: string;
  is_indian_origin: boolean;
  geographical_origin?: string;
  traditional_knowledge_associated: boolean;
  associated_tk_details?: string;
  intended_use: string;
  commercialization_intent: boolean;
  user_entity_type: string;
  jurisdiction?: string;
}

export interface ABSAssessResponse {
  biological_resource: string;
  traditional_knowledge: "Yes" | "No" | "Uncertain" | string;
  abs_review: string;
  relevant_framework: string;
  next_steps: string[];
  sources: SourceRef[];
  confidence: "HIGH" | "MEDIUM" | "LOW" | string;
  confidence_score: number;
  abstained?: boolean;
  abstention_reason?: string;
  disclaimer: string;
}

// ============================================================
// Step 7: TKDL & Prior Art Discovery Types
// ============================================================

export interface TKPriorArtRequest {
  formulation?: string;
  ingredients?: string;
  traditional_use?: string;
  therapeutic_claim?: string;
  keywords?: string;
  jurisdiction?: string;
}

export interface PriorArtPointer {
  database_name: string;
  access_type: string;
  search_url?: string;
  recommended_search_strategy: string;
  access_note: string;
}

export interface TKPriorArtResponse {
  traditional_knowledge: string;
  potential_prior_art: string;
  retrieved_evidence: SourceRef[];
  sources: SourceRef[];
  database_pointers: PriorArtPointer[];
  next_step: string;
  confidence: string;
  confidence_score: number;
  abstained?: boolean;
  disclaimer: string;
}

// ============================================================
// Core fetch helper
// ============================================================

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorBody.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ============================================================
// API Functions
// ============================================================

/** Ask a source-cited question (POST /api/chat) */
export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/** Upload a PDF document (POST /api/upload) */
export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorBody.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<UploadResponse>;
}

/** Analyze an uploaded document (POST /api/document/analyze) */
export async function analyzeDocument(
  request: DocumentAnalyzeRequest
): Promise<DocumentAnalyzeResponse> {
  return apiFetch<DocumentAnalyzeResponse>("/document/analyze", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/** List all knowledge-base sources (GET /api/sources) */
export async function getSources(jurisdiction?: string): Promise<SourcesResponse> {
  const q = jurisdiction ? `?jurisdiction=${encodeURIComponent(jurisdiction)}` : "";
  return apiFetch<SourcesResponse>(`/sources${q}`, { method: "GET" });
}

/** Submit feedback (POST /api/feedback) */
export async function submitFeedback(
  request: FeedbackRequest
): Promise<{ ok: boolean; message_id: string }> {
  return apiFetch("/feedback", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getHealth(): Promise<HealthResponse> {
  const baseUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api").replace(/\/api\/?$/, "");
  const res = await fetch(`${baseUrl}/health`);
  return res.json();
}

/** Business Profiles */
export async function createProfile(data: BusinessProfile): Promise<BusinessProfile> {
  return apiFetch<BusinessProfile>("/profile", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getProfiles(): Promise<BusinessProfile[]> {
  return apiFetch<BusinessProfile[]>("/profile", { method: "GET" });
}

export async function getProfile(id: string): Promise<BusinessProfile> {
  return apiFetch<BusinessProfile>(`/profile/${id}`, { method: "GET" });
}

export async function updateProfile(id: string, data: Partial<BusinessProfile>): Promise<BusinessProfile> {
  return apiFetch<BusinessProfile>(`/profile/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getCompliancePassport(id: string): Promise<CompliancePassport> {
  return apiFetch<CompliancePassport>(`/profile/${id}/passport`, { method: "GET" });
}

/** Step 5: AYUSH Formulation Classification */
export async function classifyAYUSH(request: AYUSHClassifyRequest): Promise<AYUSHClassifyResponse> {
  return apiFetch<AYUSHClassifyResponse>("/tk-risk/classify", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/** Traditional Knowledge Risk Assessment */
export async function assessTKRisk(request: TKRiskRequest): Promise<TKRiskResponse> {
  return apiFetch<TKRiskResponse>("/tk-risk/assess", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getReferenceHerbs(): Promise<string[]> {
  return apiFetch<string[]>("/tk-risk/reference-herbs", { method: "GET" });
}

/** Step 6: Biological Resource & ABS Assessor */
export async function assessABS(request: ABSAssessRequest): Promise<ABSAssessResponse> {
  return apiFetch<ABSAssessResponse>("/features/abs-assess", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/** Step 7: TKDL & Prior-Art Discovery Aid */
export async function searchTKPriorArt(request: TKPriorArtRequest): Promise<TKPriorArtResponse> {
  return apiFetch<TKPriorArtResponse>("/features/tk-prior-art", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
