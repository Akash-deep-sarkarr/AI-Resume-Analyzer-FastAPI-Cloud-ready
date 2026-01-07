from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    resume_summary: str
    job_description: str
    match_score: float  # percentage 0–100
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    raw_similarity: float
    skill_coverage: float
    resume_cloud_path: Optional[str] = None
