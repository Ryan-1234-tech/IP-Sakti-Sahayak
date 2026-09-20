# IP-SAKTI Sahayak — Manual Setup, Knowledge Base Curation & Demo Guide

This document lists all **explicit manual steps** required by the team to configure API keys, curate official government PDFs, enable OCR, and rehearse the live hackathon demonstrations.

---

## 1. Environment & API Keys Configuration

### Step 1.1: Backend Configuration
1. Navigate to the `backend` folder:
   ```powershell
   cd backend
   ```
2. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
3. Open `backend/.env` in any text editor and fill in your keys:
   ```ini
   # Required for live LLM grounded responses and translation
   ANTHROPIC_API_KEY=sk-ant-api03-xxxx...
   
   # Optional overrides (defaults will work out of the box)
   CLAUDE_MODEL=claude-3-5-sonnet-20241022
   CHROMA_PERSIST_DIR=./data/chroma_db
   DATABASE_URL=sqlite+aiosqlite:///./ip_sakti.db
   ```

### Step 1.2: Frontend Configuration
1. Navigate to `frontend`:
   ```powershell
   cd frontend
   ```
2. Copy `.env.example` to `.env.local`:
   ```powershell
   copy .env.example .env.local
   ```
3. Ensure the backend URL points to `http://localhost:8000/api`.

---

## 2. Curating Knowledge Base PDFs (Manual Step for Member 6)

For high-precision grounded answers and reliable citations, curate **15 to 25 official PDFs** from government portals rather than automated crawling.

### Recommended Document Sources:
1. **IP India (Controller General of Patents, Designs and Trade Marks)**:
   - *Manual of Patent Office Practice and Procedure* (Chapters on Section 3(d), 3(p) Patentability).
   - *Draft Guidelines for Examination of Patent Applications in the Field of Traditional Knowledge and Biological Material*.
   - *Trade Marks Act 1999 & Manual of Trade Marks Practice and Procedure* (Section 9 and Section 11 grounds).
   - *Fee Schedule & Concessions for MSMEs/Startups*.
   - URL: `https://ipindia.gov.in/`
2. **Ministry of AYUSH**:
   - *Guidelines for Good Manufacturing Practices (GMP) for ASU Drugs (Schedule T)*.
   - *Regulatory Framework for AYUSH Startups and Licensing Procedure*.
   - *Labelling Rules for Ayurvedic & Herbal Formulations (Rule 161)*.
   - URL: `https://ayush.gov.in/`
3. **Traditional Knowledge Digital Library (TKDL) & WIPO**:
   - *TKDL Access and Protection Guidelines*.
   - *PCT Applicant’s Guide — Indian National Phase Filing Guidelines*.
   - URL: `https://www.tkdl.res.in/` & `https://www.wipo.int/pct/`

### How to Add & Sidecar Documents:
1. Place downloaded PDFs into `backend/data/pdfs/`.
2. Name them descriptively, e.g.:
   - `ipindia_patent_tk_guidelines_2023.pdf`
   - `ipindia_trademark_manual_objections_2022.pdf`
   - `ayush_gmp_schedule_t_manual_2021.pdf`
3. *(Optional but Recommended)* Create a sidecar JSON file alongside the PDF (e.g. `backend/data/pdfs/ipindia_patent_tk_guidelines_2023.json`):
   ```json
   {
     "title": "Guidelines for Examination of Traditional Knowledge and Biological Material",
     "authority": "IP India",
     "url": "https://ipindia.gov.in/writereaddata/Portal/IPOGuidelines/1_37_1_guidelines-traditional-knowledge.pdf",
     "document_type": "guideline",
     "topic": "patents_ayush",
     "publication_date": "2023"
   }
   ```
4. Run the ingestion script:
   ```powershell
   cd backend
   .\venv\Scripts\python scripts/ingest.py
   ```

---

## 3. Optical Character Recognition (OCR) Prerequisites (Manual)

If you plan to demo scanned / non-selectable PDF notices:
- **Windows**:
  1. Download Tesseract Windows installer: `https://github.com/UB-Mannheim/tesseract/wiki`
  2. Install to default path: `C:\Program Files\Tesseract-OCR`
  3. Ensure `tesseract.exe` is added to your System `PATH` variable.
  4. Ensure Hindi language pack (`hin.traineddata`) is checked during installation if Hindi scan reading is required.
- **Linux/Mac**:
  ```bash
  sudo apt-get install tesseract-ocr tesseract-ocr-hin
  # Or on macOS:
  brew install tesseract tesseract-lang
  ```

> *Note: For high reliability during a live hackathon demo, prioritize text-based PDFs (which extract instantly via PyMuPDF without OCR overhead).*

---

## 4. Preparing 3 Curated Demo Scenarios (For Live Pitch)

### 🎯 Demo 1: Multilingual AYUSH Patent & Traditional Knowledge Query
- **User Persona**: Ayurvedic formulation inventor speaking **Tamil**.
- **Action**: Speak or paste in Tamil:
  > *"நான் ஒரு புதிய ஆயுர்வேத மூலிகை சூத்திரத்திற்கு (Ashwagandha + Curcumin) காப்புரிமை (Patent) பெற முடியுமா?"*
- **What to highlight to judges**:
  1. Instant translation and grounded RAG retrieval from IP India TK Guidelines.
  2. Answer delivered back in Tamil citing Section 3(p) of the Patents Act.
  3. **Traditional Knowledge Sensitivity Indicator** showing "Medium/High sensitivity" (advising novel extraction/synergy rather than raw herb mix).
  4. **High Confidence** badge with source cards.

---

### 🎯 Demo 2: Document Intelligence (Notice-to-Action Converter)
- **User Persona**: MSME Founder who received a Trademark Objection Notice.
- **Action**: Drag and drop sample notice PDF (`sample_trademark_exam_report.pdf`).
- **What to highlight to judges**:
  1. Fast PDF text extraction + Section 9(1)(a) objection detection.
  2. Automatic extraction of 30-day response deadline.
  3. Plain-language conversion: "The examiner flagged the name as descriptive."
  4. Instant **Step-by-step Action Checklist** (User Affidavit, Prior Sales Invoices, Response Drafting guidelines).

---

### 🎯 Demo 3: Compliance Digital Twin & Regulation Impact
- **User Persona**: AYUSH Herbal Startup launching a skincare formulation.
- **Action**: Open Digital Twin Profile, select *Ayurveda*, Stage: *Ready to Launch*.
- **What to highlight to judges**:
  1. Live **Compliance Passport** generated with mandatory AYUSH Drug Licence (Form 24D) and Rule 161 labelling compliance.
  2. Simulate a new government notification (e.g. *Revised Heavy Metal Limits in Herbal Extracts*).
  3. System triggers an **Impact Alert** explicitly stating *why* this applies to their formulation and the exact deadline to update testing records.
  4. One-click **Expert Review Brief** export for sharing with an IP attorney.

---

## 5. Daily Development Launch Commands

### Run Backend
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Run Frontend
```powershell
cd frontend
npm run dev
```
Open [http://localhost:3000](http://localhost:3000).
