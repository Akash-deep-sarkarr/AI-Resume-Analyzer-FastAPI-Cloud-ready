from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List

from resume_processing import extract_resume_text, extract_skills_from_text
from matching import analyze_match
from schemas import AnalysisResponse
from cloud_storage import store_resume_file

app = FastAPI(title="Cloud AI Resume Analyzer & Job Matcher")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Resume analyzer backend is running"}


@app.post("/analyze_resume", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await resume.read()
    filename = resume.filename or "uploaded"
    resume_cloud_path = store_resume_file(file_bytes=file_bytes, filename=filename)
    resume_text = extract_resume_text(file_bytes=file_bytes, filename=filename)

    result = analyze_match(resume_text=resume_text, job_description=job_description)
    result["resume_cloud_path"] = resume_cloud_path
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
