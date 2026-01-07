from __future__ import annotations

from typing import List

from skills_db import SKILLS


def extract_skills(text: str) -> List[str]:
    """Extract skills from text using a simple keyword lookup over SKILLS.

    For a viva / academic project this is clear and explainable: we
    maintain a curated skill list and check membership in lowercased text.
    """
    lowered = text.lower()
    return [skill for skill in SKILLS if skill in lowered]
