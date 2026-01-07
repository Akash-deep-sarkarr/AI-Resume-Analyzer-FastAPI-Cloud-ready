from __future__ import annotations

from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills


_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _load_model() -> Optional[SentenceTransformer]:
    try:
        return SentenceTransformer(_MODEL_NAME)
    except Exception:
        # If the model cannot be loaded (no internet, etc.), fall back to TF-IDF only
        return None


_model: Optional[SentenceTransformer] = _load_model()


def _embed_with_model(texts: List[str]) -> np.ndarray:
    assert _model is not None
    return _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def _embed_with_tfidf(texts: List[str]) -> np.ndarray:
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    # Normalize each row vector
    norms = np.linalg.norm(matrix.toarray(), axis=1, keepdims=True) + 1e-9
    return matrix.toarray() / norms


def _compute_similarity(resume_text: str, job_description: str) -> float:
    texts = [resume_text, job_description]
    if _model is not None:
        embeddings = _embed_with_model(texts)
    else:
        embeddings = _embed_with_tfidf(texts)

    sim = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
    # Clamp to [0, 1]
    sim = max(0.0, min(1.0, sim))
    return sim


def analyze_match(resume_text: str, job_description: str) -> dict:
    """Core AI logic to compute match score and suggestions."""
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    resume_skill_set = set(s.lower() for s in resume_skills)
    jd_skill_set = set(s.lower() for s in jd_skills)

    matched_skills = sorted({s for s in jd_skills if s.lower() in resume_skill_set})
    missing_skills = sorted({s for s in jd_skills if s.lower() not in resume_skill_set})

    similarity = _compute_similarity(resume_text, job_description)

    # Skill match score: how many JD skills are present in the resume
    skill_match_score = 0.0
    if jd_skill_set:
        skill_match_score = len(matched_skills) / max(1, len(jd_skill_set))

    # Final score combines semantic similarity and skill overlap
    match_score = 0.6 * similarity + 0.4 * skill_match_score
    match_score_percentage = round(match_score * 100, 2)

    suggestions: List[str] = []
    if missing_skills:
        suggestions.append(
            "Consider adding or highlighting these skills if you have experience with them: "
            + ", ".join(missing_skills)
        )
    if skill_match_score < 0.4:
        suggestions.append(
            "Add a dedicated Skills section aligned with the job role and make sure key keywords are clearly visible."
        )
    if match_score < 0.6:
        suggestions.append(
            "Tailor your resume summary and experience bullets to match key responsibilities in the job description."
        )
    if not jd_skills:
        suggestions.append(
            "The job description does not contain many recognized technical skills; focus on aligning responsibilities and achievements."
        )

    return {
        "resume_summary": resume_text[:500] + ("..." if len(resume_text) > 500 else ""),
        "job_description": job_description,
        "match_score": match_score_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "raw_similarity": similarity,
        "skill_coverage": skill_match_score,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
    }
