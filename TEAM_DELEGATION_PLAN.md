# IP-SAKTI Sahayak — 6-Member Team Delegation & Execution Plan

This guide establishes clear role ownership, Git branch strategy, interface contracts, and task breakdowns so all 6 members can build concurrently with zero merge conflicts.

---

## 1. Team Roles & Ownership Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TEAM ALLOCATION                                        │
├──────────────────────────────┬─────────────────────────────────────────────────────────┤
│ Member 1: Frontend Lead      │ Digital Twin Dashboard, Compliance Passport, Calendar   │
│ Member 2: Frontend Engineer  │ Multilingual Chat, Voice STT/TTS, Expert Brief UI       │
│ Member 3: Doc Intelligence   │ PDF Notice Parser, Section 9/11 Extractor, OCR Fallback │
│ Member 4: RAG & AI Lead      │ Curated RAG Engine, Evidence Grounding, TK Risk Scorer  │
│ Member 5: Backend Core       │ Digital Twin APIs, Profile Store, Regulation Impact     │
│ Member 6: QA & Knowledge     │ Official PDF Curation, Demo Scenarios, Ingestion Seed   │
└──────────────────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Member Breakdown & Deliverables

### 👤 Member 1: Frontend Lead (Digital Twin & Compliance Passport UI)
- **Primary Focus**: Digital Twin Profile setup and Compliance Passport dashboard.
- **Key Files Owned**:
  - `frontend/components/CompliancePassport.tsx` *(New)*
  - `frontend/components/ProfileDrawer.tsx` *(New)*
  - `frontend/components/ComplianceCalendar.tsx` *(New)*
  - `frontend/app/dashboard/page.tsx` or main tab switcher in `frontend/app/page.tsx`
- **Deliverables**:
  1. Profile onboarding form (Business Type, AYUSH stream, Brand, Formulation, Stage).
  2. Compliance Passport visual widget: Active IP status rings, required licences (AYUSH Form 24D/CoPP), checklist.
  3. Interactive Compliance Calendar tracking upcoming deadlines and renewal dates.
- **Git Branch**: `feat/frontend-digital-twin`

---

### 👤 Member 2: Frontend Engineer (Multilingual Chat, Voice & Expert Brief)
- **Primary Focus**: Chat experience, Web Speech voice I/O, Notice-to-Action display, and Expert Brief modal.
- **Key Files Owned**:
  - `frontend/components/ChatInput.tsx` (Voice STT / Language toggles)
  - `frontend/components/ChatMessage.tsx` & `frontend/components/SourceCard.tsx`
  - `frontend/components/ExpertBriefModal.tsx` *(New)*
  - `frontend/lib/speech.ts` *(New: TTS speaker helper for Hindi/Tamil/English)*
- **Deliverables**:
  1. Speech-to-Text with instant language switching (English, Hindi, Tamil).
  2. Text-to-Speech audio readout for grounded answers.
  3. "Export Expert Brief" button that generates a downloadable case brief for attorneys.
  4. Notice-to-Action interactive checklist (checkboxes for user tasks).
- **Git Branch**: `feat/frontend-voice-brief`

---

### 👤 Member 3: Document Intelligence & OCR Specialist
- **Primary Focus**: Parsing uploaded PDF notices, extraction of legal clauses, dates, objection grounds.
- **Key Files Owned**:
  - `backend/app/services/document_intel.py`
  - `backend/app/services/notice_parser.py` *(New)*
  - `backend/app/routers/document.py`
- **Deliverables**:
  1. Rule-based + LLM parsing of **Trademark Examination Reports** (Extracts: App No, Class, Section 9(1)(a) absolute grounds vs Section 11(1) relative grounds, conflicting marks, 30-day deadline).
  2. Extraction of **Patent Office FER (First Examination Report)** objections (Section 3(d), Section 3(p) TK grounds).
  3. Notice-to-Action structured generator: plain-language explanation + step-by-step response strategy.
- **Git Branch**: `feat/doc-intel-parser`

---

### 👤 Member 4: AI & RAG Engine Lead
- **Primary Focus**: Retrieval precision, evidence grounding, confidence rubric, and Traditional Knowledge risk evaluator.
- **Key Files Owned**:
  - `backend/app/services/rag.py`
  - `backend/app/services/confidence.py`
  - `backend/app/services/tk_risk.py` *(New)*
  - `backend/app/services/vector_store.py` & `backend/app/services/embeddings.py`
- **Deliverables**:
  1. Section/Rule citation extractor: ensures answers pinpoint exact sections (e.g. *Section 3(p) Patents Act*, *Rule 161 D&C Rules*).
  2. Traditional Knowledge (TK) Risk Scorer: takes ingredients + claims and scores sensitivity (High/Med/Low) with non-patentability warnings.
  3. Verification & Confidence Scorer enhancement (incorporates primary vs secondary source weighting).
- **Git Branch**: `feat/rag-tk-engine`

---

### 👤 Member 5: Backend Core & Business Engine Lead
- **Primary Focus**: Digital Twin profile state, Regulation Impact Engine, and API persistence.
- **Key Files Owned**:
  - `backend/app/models/db.py` & `backend/app/models/schemas.py`
  - `backend/app/routers/profile.py` *(New)*
  - `backend/app/routers/regulation.py` *(New)*
  - `backend/app/services/regulation_impact.py` *(New)*
  - `backend/app/main.py`
- **Deliverables**:
  1. Digital Twin profile REST APIs: `GET/POST /api/profile`, `GET /api/profile/passport`.
  2. Regulation Change Impact Engine: `POST /api/regulation/impact` (matches notification against profile attributes and generates tailored impact notices).
  3. Compliance Calendar API: `GET /api/calendar/deadlines`.
- **Git Branch**: `feat/backend-digital-twin`

---

### 👤 Member 6: Knowledge Curation, Data & QA Lead
- **Primary Focus**: Curating 20–30 official government PDFs, metadata sidecars, test notices, and running demo rehearsals.
- **Key Files Owned**:
  - `backend/data/pdfs/` (Curated documents)
  - `backend/data/sample_notices/` (Test PDFs for Trademark/Patent notices)
  - `backend/scripts/ingest.py`
  - `DEMO_SCRIPT.md` *(New)*
- **Deliverables**:
  1. Download and organize 25 official PDFs (IP India Guidelines, AYUSH GMP Circulars, TKDL Information, Trademark Manual).
  2. Create JSON sidecar files with exact `authority`, `url`, `document_type`, `topic`.
  3. Run and verify `python scripts/ingest.py`.
  4. Prepare 3 mock examination notices for live PDF upload demos.
  5. Script and rehearse the 3 live hackathon demo journeys.
- **Git Branch**: `feat/knowledge-data-qa`

---

## 3. Git Workflow & Collaboration Rules

### Branch Strategy
1. **`main`**: Protected branch. Always deployable and tested.
2. **Feature branches**:
   - `feat/frontend-digital-twin` (Member 1)
   - `feat/frontend-voice-brief` (Member 2)
   - `feat/doc-intel-parser` (Member 3)
   - `feat/rag-tk-engine` (Member 4)
   - `feat/backend-digital-twin` (Member 5)
   - `feat/knowledge-data-qa` (Member 6)

### How to Work in Parallel
```bash
# Clone the repository
git clone <REPO_URL>
cd ip-sakti-sahayak

# Create your feature branch
git checkout -b feat/<your-branch-name>

# Pull latest changes from main before starting work
git pull origin main

# Commit small, descriptive chunks
git add .
git commit -m "feat(module): add specific capability"
git push -u origin feat/<your-branch-name>
```

---

## 4. API & Shared Schema Contracts (Zero-Conflict Interfaces)

To prevent frontend and backend blockers, follow these predefined schema contracts:

### A. Digital Twin Profile (`/api/profile`)
```typescript
export interface BusinessProfile {
  id?: string;
  business_name: string;
  entity_type: "innovator" | "startup" | "msme" | "manufacturer" | "researcher";
  state_location: string;
  ayush_category: "ayurveda" | "siddha" | "unani" | "homeopathy" | "yoga" | "other";
  stage: "ideation" | "formulation_rd" | "ready_to_launch" | "commercialized";
  brand_name?: string;
  product_claims?: string;
  formulation_summary?: string;
  active_ip_assets: Array<{
    type: "trademark" | "patent" | "copyright" | "design";
    application_number: string;
    status: string;
    filing_date?: string;
    deadline_date?: string;
  }>;
}
```

### B. Compliance Passport (`/api/profile/passport`)
```typescript
export interface CompliancePassport {
  profile_id: string;
  ip_routes: Array<{ route: string; rationale: string; priority: "HIGH" | "MEDIUM" | "LOW" }>;
  ayush_obligations: Array<{ licence_name: string; authority: string; form_no: string }>;
  action_checklist: Array<{ step: number; task: string; deadline?: string; completed: boolean }>;
  compliance_score: number; // 0 - 100
}
```

### C. Traditional Knowledge (TK) Risk (`/api/tk/evaluate`)
```typescript
export interface TKEvaluationRequest {
  formulation_name: string;
  ingredients: string[];
  preparation_method: string;
  therapeutic_claim: string;
}

export interface TKEvaluationResponse {
  sensitivity_level: "LOW" | "MEDIUM" | "HIGH";
  reasoning: string;
  prior_art_advisory: string;
  section_3p_applicability: boolean;
  recommended_path: string;
}
```
