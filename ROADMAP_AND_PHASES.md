# IP-SAKTI Sahayak — Architectural Roadmap & Implementation Phases

**Explainable IP & AYUSH Compliance Digital Twin**  
*Trust → Evidence → Explanation → Action*

---

## 1. Executive Status: What Is Done vs. What Needs To Be Done

### ✅ What Is Already Built & Verified (Baseline MVP)
1. **Monorepo Architecture**:
   - **Backend**: FastAPI with async SQLAlchemy (SQLite), FAISS vector store, FastEmbed local ONNX embedding pipeline, Pydantic schemas, and modular routers.
   - **Frontend**: Next.js 16 (Turbopack) + React 19 + Tailwind CSS v4 design system with dark ambient glow, glassmorphism, responsive chat UI, and persistent legal disclaimer footer.
2. **Core RAG & Verification Engine**:
   - Cosine similarity retrieval over local vector store.
   - Grounded system prompt enforcing citations and strict non-hallucination.
   - Rule-based confidence scoring rubric (HIGH / MEDIUM / LOW) based on chunk similarity, government source authority, and hedging pattern detection.
3. **Language & Document Foundations**:
   - Basic language detection (`langdetect`) and translate-then-retrieve architecture.
   - Initial PDF text extraction using PyMuPDF (`fitz`) and OCR fallback hooks.
   - Basic Notice-to-Action schema and ActionCard UI rendering.
4. **Local Zero-Ops Readiness**:
   - Fully runs locally on Windows/Linux without requiring Visual C++ compilation.
   - FastEmbed + FAISS-CPU installed and pre-warmed.

---

### 🚀 What Needs To Be Built (Digital Twin & Advanced Engines)

| Component | Target Capability | Complexity |
|---|---|---|
| **1. Compliance Digital Twin & Passport** | Business profile state (MSME/innovator, AYUSH category, brand, active IP, stage) generating a dynamic live Compliance Passport. | Medium-High |
| **2. Expanded Knowledge & Evidence Engine** | Curated 25+ official IP India / AYUSH / WIPO documents with exact Section/Rule citations, forms, and fees. | Medium |
| **3. Deep Document Intelligence** | Specialized parser for Trademark Examination Reports & Patent Office Notices (extracting objections, Section 9/11 citations, response deadlines). | High |
| **4. Regulation Change Impact Engine** | Evaluator matching new government circulars/gazettes against user profiles to generate personalized impact alerts. | Medium |
| **5. Compliance Calendar & Timeline** | Interactive timeline tracking filing deadlines, objection reply cut-offs, renewal windows, and hearing dates. | Medium |
| **6. Traditional Knowledge (TK) Risk Indicator** | AYUSH formulation analyzer evaluating ingredients, therapeutic claims, and public domain sensitivity before patent filing. | Medium |
| **7. Expert Review Brief Generator** | One-click export of structured case briefs (PDF/Markdown) for IP attorneys or AYUSH consultants when confidence is low or risk is high. | Low-Medium |
| **8. Enhanced Multilingual & Voice UX** | Hindi, Tamil, and English audio feedback (Web Speech TTS/STT) and seamless script switching. | Low-Medium |

---

## 2. Phased Implementation Plan

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASE 1: Digital Twin & Profile Engine              │
│       (Profile onboarding, business state, Compliance Passport UI)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│              PHASE 2: Advanced Document & Objection Intelligence       │
│  (Trademark / Patent notice parsing, Section extractors, Action Engine)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│           PHASE 3: Regulation Impact, TK Risk & Calendar Engine        │
│       (Circular matcher, formulation sensitivity, deadline timeline)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│           PHASE 4: Expert Escalation, Voice & Hackathon Demo Polish    │
│       (1-click attorney brief, speech synthesis, 3 live demo journeys) │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Compliance Digital Twin & Passport (Foundation)
**Objective**: Transform from session-based chat to persistent business digital twin.

#### Tasks:
1. **Backend Database Models**:
   - `UserProfile` / `BusinessProfile`:
     - `business_name`, `entity_type` (Individual, Startup, MSME, University, Manufacturer).
     - `state_location`, `ayush_category` (Ayurveda, Siddha, Unani, Homeopathy, Yoga, Multi-herb).
     - `stage` (Ideation, Formulation/R&D, Clinical Trial, Ready to Launch, Commercialized).
     - `brand_name`, `product_claims`, `formulation_summary`.
     - `active_ip_assets` (JSON array: type, application_number, status, filing_date).
2. **Compliance Passport Generator Service**:
   - Engine that evaluates business profile + stage and generates:
     - Recommended IP protection pathways (Patent vs Trademark vs Trade Secret vs Design).
     - AYUSH regulatory obligations (GMP Schedule T compliance, AYUSH Drug Licence Form 24D/25D, CoPP certification).
     - Mandatory label compliance requirements (Rule 161 of Drugs & Cosmetics Rules).
     - Priority-tagged actionable checklist.
3. **Frontend Digital Twin UI**:
   - Profile drawer / onboarding modal with smart pre-fills.
   - **Compliance Passport View**: Visual dashboard with status rings, protection routes, and upcoming compliance milestones.

---

### Phase 2: Deep Document Intelligence & Notice-to-Action Converter
**Objective**: Parse complex government notices (especially Trademark Examination Reports and Patent Office Actions).

#### Tasks:
1. **Notice Parser**:
   - Regex + LLM extractor tuned for IP India Trademark Examination Reports:
     - Extraction of: Application Number, Class, Objected Sections (e.g. *Section 9(1)(a) Absolute Grounds* or *Section 11(1) Relative Grounds*).
     - Conflicting trademark citations cited by examiner.
     - 30-day response deadline calculation from dispatch date.
2. **Action Plan Synthesizer**:
   - Translates legal objections into plain language:
     - *What it means*: "The examiner says the name describes the product quality."
     - *How to overcome*: "Submit evidence of distinctiveness or user affidavit with prior invoices."
     - *Required documents checklist*.
3. **Frontend Notice Visualizer**:
   - Split-screen document analyzer: Uploaded PDF viewer on left, Extracted Action Plan & Official Evidence on right.

---

### Phase 3: Regulation Impact, TK Risk & Interactive Calendar
**Objective**: Continuous compliance monitoring and traditional knowledge safety assessment.

#### Tasks:
1. **Regulation Impact Engine**:
   - Repository of simulated / live government notifications (e.g., *Ministry of AYUSH notification on revised heavy metal testing*, *Draft patent amendment rules on reduced MSME fees*).
   - Matching algorithm comparing notification metadata against `BusinessProfile.ayush_category` and `entity_type`.
   - Generates "Impact Brief": High/Medium/Low impact, Affected labels/documents, Required actions.
2. **Traditional Knowledge (TK) Risk Indicator**:
   - Form for entering formulation ingredients (e.g., *Ashwagandha + Curcumin + Piperine extract*), extraction process, and therapeutic claims.
   - Evaluator assessing public domain prior art risk (Section 3(p) of Indian Patents Act: traditional knowledge not patentable as-is; novelty requires synergistic combination or novel formulation extraction).
   - Sensitivity score: High / Medium / Low + Recommended pathway (Novel formulation patent vs AYUSH trademark protection).
3. **Compliance Calendar Component**:
   - Interactive calendar / Gantt timeline displaying:
     - Trademark objection response deadlines.
     - Patent annuity renewal dates.
     - AYUSH GMP audit / renewal dates.

---

### Phase 4: Expert Escalation, Voice Interaction & Demo Polish
**Objective**: Production-grade presentation, expert handoff, and multi-modal interaction.

#### Tasks:
1. **Human Escalation & Expert Review Brief**:
   - Auto-triggers when confidence is `LOW` or objection is high complexity.
   - Generates downloadable, beautifully formatted **Expert Case Brief (PDF / Markdown)** containing:
     - Business Context & Product Description.
     - Extracted Legal Issue & Cited Section.
     - Timeline / Impending Deadline.
     - Recommended questions for IP Attorney / AYUSH Consultant.
2. **Voice Synthesis (TTS) & Multilingual Polish**:
   - Web Speech Synthesis for spoken answers in English, Hindi, and Tamil.
   - Toggleable language selector across all dashboard cards.
3. **Curated Demo Scenarios Verification**:
   - Demo 1: Tamil speech query on Ayurvedic formulation patentability & TKDL sensitivity.
   - Demo 2: Upload real Trademark Section 9/11 Examination Notice PDF → Instant 30-day Action Plan.
   - Demo 3: MSME Startup onboarding → Auto-generated Compliance Passport & Regulation Alert.
