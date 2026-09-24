import re
from typing import Any

from config import EXCLUDED_TERMS, TARGET_LOCATIONS, TARGET_ROLES, TARGET_SKILLS


def normalize(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").lower())


def _has_phrase(text: str, phrase: str) -> bool:
    return phrase.lower() in text


def _experience_score(full_text: str) -> int:
    ranges = re.findall(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years|yrs)", full_text)
    single = re.findall(r"(\d+)\+?\s*(?:years|yrs)", full_text)
    for lo, hi in ranges:
        lo, hi = int(lo), int(hi)
        if lo <= 3 <= hi or lo <= 4 <= hi or lo <= 5 <= hi:
            return 10
    for years in single:
        y = int(years)
        if 2 <= y <= 5:
            return 10
        if y == 6:
            return 5
        if y >= 7:
            return -15
    return 5


def calculate_match(job: dict) -> tuple[int, list[str], list[str], list[str], list[str]]:
    title = normalize(job.get("title"))
    location = normalize(job.get("location"))
    description = normalize(job.get("description"))
    full_text = f"{title} {location} {description}"

    # 100-point score: role 35 + location 20 + skills 35 + experience 10.
    role_hits = [r for r in TARGET_ROLES if _has_phrase(title, r)]
    location_hits = [loc for loc in TARGET_LOCATIONS if _has_phrase(full_text, loc)]
    skill_hits = [s for s in TARGET_SKILLS if _has_phrase(full_text, s)]

    score = 0
    if role_hits:
        score += 35
        # Exact-ish title quality bonus inside the role component.
        if any(title == r or title.startswith(r) for r in role_hits):
            score += 5

    if location_hits:
        score += 20

    score += min(len(skill_hits) * 4, 35)
    score += _experience_score(full_text)

    negative_hits = [x for x in EXCLUDED_TERMS if _has_phrase(full_text, x)]
    score -= min(len(negative_hits) * 20, 40)

    score = max(0, min(int(score), 100))
    return score, skill_hits, role_hits, location_hits, negative_hits


def match_job(job: dict[str, Any]) -> dict[str, Any]:
    score, skills, roles, locations, negatives = calculate_match(job)
    job["match_score"] = score
    job["matched_skills"] = skills
    job["matched_roles"] = roles
    job["matched_locations"] = locations
    job["negative_terms"] = negatives
    return job
    return job
