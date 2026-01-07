from __future__ import annotations

import io
from typing import List

import fitz  # PyMuPDF
from docx import Document


# A simple list of common technical skills and tools.
# In a real system this could come from a database or configurable source.
SKILL_KEYWORDS: List[str] = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "react",
    "node.js",
    "node",
    "django",
    "flask",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "machine learning",
    "deep learning",
    "nlp",
    "pandas",
    "numpy",
    "scikit-learn",
    "git",
    "rest api",
    "microservices",
]


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    text_chunks: List[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    return "\n".join(text_chunks)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    file_stream = io.BytesIO(file_bytes)
    doc = Document(file_stream)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from a resume file (PDF or DOCX or plain text)."""
    lower_name = filename.lower()
    try:
        if lower_name.endswith(".pdf"):
            text = _extract_text_from_pdf(file_bytes)
        elif lower_name.endswith(".docx"):
            text = _extract_text_from_docx(file_bytes)
        else:
            # Fallback: try to decode as UTF-8 text
            text = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        # Very defensive fallback
        text = file_bytes.decode("utf-8", errors="ignore")

    return _clean_text(text)


def _clean_text(text: str) -> str:
    # Basic cleanup: normalize whitespace
    return " ".join(text.split())


def extract_skills_from_text(text: str) -> List[str]:
    """Very simple keyword-based skill extraction.

    For a viva/demo this is enough to show the concept; it can be
    replaced later by an NER model or more advanced NLP.
    """
    lowered = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        if skill.lower() in lowered:
            found.append(skill)
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for s in found:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique
