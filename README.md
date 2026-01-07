# AI-Resume-Analyzer-FastAPI-Cloud-ready

Cloud-based AI Resume Analyzer and Intelligent Job Matching System built with FastAPI, sentence-transformers, and a modern Tailwind-powered dashboard. The app is designed as a SaaS-ready, one-agent architecture that can be deployed to free cloud platforms.

## Overview

This project automatically:
- **Parses resumes** (PDF/DOCX/TXT)
- **Extracts skills** from both resume and job description
- **Computes a hybrid match score** combining semantic similarity and skill overlap
- **Highlights matched and missing skills**
- **Generates AI-style recommendations** to improve the resume

The frontend is a glassmorphism-inspired UI with drag-and-drop upload, skill chips, circular match ring, and charts. The backend is cloud-ready (S3/Firebase-style object storage, FastAPI REST API) and can serve the frontend directly.

## Tech Stack

- **Backend**
  - Python
  - FastAPI
  - sentence-transformers (`all-MiniLM-L6-v2`)
  - scikit-learn, NumPy
  - PyMuPDF (PDF), python-docx (DOCX)
  - boto3 (optional S3 storage)

- **Frontend**
  - HTML + Tailwind CSS (CDN)
  - Vanilla JavaScript
  - Chart.js (Radar + Bar charts)

- **Cloud-Ready Architecture**
  - REST API (`/analyze_resume`)
  - Static frontend served via FastAPI `StaticFiles` at `/frontend/`
  - Optional resume storage in S3 (`cloud_storage.py`)

## Project Structure

```text
backend/
  app.py              # FastAPI app, mounts /frontend and exposes /analyze_resume
  resume_processing.py# PDF/DOCX/text extraction & cleaning
  skills_db.py        # Central skills database
  skill_extractor.py  # Keyword-based skill extraction
  matching.py         # Hybrid matching (semantic + skills)
  cloud_storage.py    # Optional S3 upload for resumes
  schemas.py          # Pydantic response models
  requirements.txt    # Backend dependencies

frontend/
  index.html          # Tailwind UI (hero, upload card, results dashboard)
  app.js              # Drag & drop, API calls, charts, skill chips
  styles.css          # Minimal base styling
```

## How the AI Matching Works

1. **Text Extraction**
   - Uses PyMuPDF or python-docx (or plain text) to extract and clean resume text.
2. **Skill Extraction**
   - Looks up skills from `SKILLS` list in [`skills_db.py`](backend/skills_db.py) using simple keyword matching.
   - Extracts skills from both **resume** and **job description**.
3. **Semantic Similarity**
   - Uses `sentence-transformers/all-MiniLM-L6-v2` (or TF-IDF fallback) to embed resume and JD.
   - Computes cosine similarity between embeddings.
4. **Skill Overlap Score**

   \[
   \text{skill\_match\_score} = \frac{\lvert\text{matched JD skills}\rvert}{\max(\lvert\text{JD skills}\rvert, 1)}
   \]

5. **Final Match Score**

   \[
   \text{final\_score} = 0.6 \cdot \text{semantic\_similarity} + 0.4 \cdot \text{skill\_match\_score}
   \]

6. **Output**
   - `match_score` (0–100)
   - `matched_skills`, `missing_skills`
   - `resume_skills`, `jd_skills`
   - `suggestions` (LLM-style but rule-based)

## Running Locally

### 1. Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

### 2. Frontend

Once the backend is running, open in your browser:

```text
http://localhost:8001/frontend/
```

Then:
- Drag & drop a resume (PDF/DOCX/TXT) into the upload card
- Paste a **structured** job description, e.g.:

```text
Assistant Professor – Computer Science
Required Skills:
- Python
- Data Structures
- DBMS
- Machine Learning
- Research Publications
- Teaching Experience
```

- Click **Analyze Match** to see:
  - Circular match ring
  - Matched & missing skill chips
  - Radar & bar charts
  - AI recommendations

## Cloud & SaaS Angle (For Viva)

- **SaaS**: Multi-user web app exposed via REST API, frontend served from the same FastAPI service.
- **Cloud Storage**: `cloud_storage.py` integrates with S3 (or similar) using `boto3` to store resumes.
- **Hosting**: Can be deployed to Render/EC2/Other PaaS using the `uvicorn app:app` start command.
- **Scalability**: Stateless API with external object storage; horizontal scaling via multiple app instances.

## Viva / Presentation Pointers

- Emphasize the combination of **AI (NLP embeddings + skills)** with **Cloud (SaaS + storage)**.
- Walk through the **flow**: Upload → Parse → Extract skills → Compute similarity → Score → Suggestions → Charts.
- Highlight that the system is **one-agent**, making development and debugging simpler while still being cloud-ready.
