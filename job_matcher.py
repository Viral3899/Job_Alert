import re
from config import TARGET_ROLES, TARGET_LOCATIONS, TARGET_SKILLS, EXCLUDED_TERMS

def normalize(text):
    return re.sub(r"\s+", " ", text.lower())

def calculate_match(job):
    title = normalize(job["title"])
    location = normalize(job["location"])
    description = normalize(job["description"])
    full_text = f"{title} {location} {description}"

    score = 0

    if any(role in title for role in TARGET_ROLES):
        score += 35

    if any(loc in full_text for loc in TARGET_LOCATIONS):
        score += 20

    matched_skills = [s for s in TARGET_SKILLS if s.lower() in full_text]
    score += min(len(matched_skills) * 4, 40)

    m = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*years", full_text)
    if m and int(m.group(1)) <= 3 <= int(m.group(2)):
        score += 5

    if any(term in full_text for term in EXCLUDED_TERMS):
        score -= 40

    return max(0, min(score, 100)), matched_skills

def match_job(job):
    score, skills = calculate_match(job)
    job["match_score"] = score
    job["matched_skills"] = skills
    return job
