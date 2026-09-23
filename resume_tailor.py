import json
import os
import re
import tempfile
from pathlib import Path

import requests
from docx import Document

from config import GROQ_API_KEY, GROQ_MODEL

BASE_RESUME = Path(__file__).with_name("resume_template.docx")


def _read_base_resume():
    doc = Document(str(BASE_RESUME))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def tailor_resume(job):
    """Create a JD-specific ATS resume without inventing experience."""
    if not GROQ_API_KEY:
        print("GROQ_API_KEY missing; cannot generate tailored resume.")
        return None

    base = _read_base_resume()
    jd = job.get("description", "")
    title = job.get("title", "AI/ML Engineer")
    company = job.get("company", "Unknown")

    prompt = f"""
You are an ATS resume editor. Tailor the candidate resume below to the exact job description.

STRICT RULES:
1. NEVER invent employers, dates, degrees, certifications, tools, projects, metrics, or responsibilities.
2. Only use facts explicitly present in the base resume.
3. You may reorder existing skills and rewrite bullets to emphasize facts relevant to the JD.
4. Do not claim a tool/skill merely because it is similar to another tool.
5. Keep the candidate's name/contact information unchanged.
6. Keep all employment dates and employer names unchanged.
7. Make the resume ATS-friendly and concise, ideally 1-2 pages.
8. Use the exact JD terminology when it accurately describes an existing skill.
9. If a JD requirement is missing from the base resume, do not add it.
10. Return JSON only.

JOB TITLE: {title}
COMPANY: {company}

JOB DESCRIPTION:
{jd[:18000]}

BASE RESUME:
{base[:30000]}

Return exactly this JSON structure:
{{
  "headline": "...",
  "summary": "...",
  "skills": ["category: skill1, skill2"],
  "experience": [
    {{"role": "...", "company": "...", "dates": "...", "bullets": ["...", "..."]}}
  ],
  "projects": [
    {{"name": "...", "stack": "...", "bullets": ["..."]}}
  ],
  "education": ["..."]
}}
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return _extract_json(content)


def build_resume_docx(job, tailored):
    safe_company = re.sub(r"[^A-Za-z0-9]+", "_", job.get("company", "Company")).strip("_")
    safe_title = re.sub(r"[^A-Za-z0-9]+", "_", job.get("title", "Role")).strip("_")
    filename = f"Viral_Sherathiya_{safe_company}_{safe_title}_Tailored_Resume.docx"[:180]
    path = Path(tempfile.gettempdir()) / filename

    doc = Document()
    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = __import__("docx").shared.Pt(9)

    p = doc.add_paragraph()
    p.alignment = 1
    r = p.add_run("VIRAL SHERATHIYA")
    r.bold = True
    r.font.size = __import__("docx").shared.Pt(18)

    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(tailored.get("headline", "AI/ML ENGINEER")).bold = True

    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run("Ahmedabad, Gujarat, India | +91-8140408415 | viralsherathiya1008@gmail.com | linkedin.com/in/viralsherathiya | github.com/Viral3899")

    def heading(text):
        p = doc.add_paragraph()
        r = p.add_run(text.upper())
        r.bold = True
        r.font.size = __import__("docx").shared.Pt(11)

    heading("Professional Summary")
    doc.add_paragraph(tailored.get("summary", ""))

    heading("Core Skills")
    for item in tailored.get("skills", []):
        doc.add_paragraph(item, style="List Bullet")

    heading("Professional Experience")
    for exp in tailored.get("experience", []):
        p = doc.add_paragraph()
        r = p.add_run(f"{exp.get('role','')} — {exp.get('company','')}")
        r.bold = True
        p.add_run(f" | {exp.get('dates','')}")
        for bullet in exp.get("bullets", []):
            doc.add_paragraph(bullet, style="List Bullet")

    heading("Selected Projects")
    for project in tailored.get("projects", []):
        p = doc.add_paragraph()
        r = p.add_run(project.get("name", ""))
        r.bold = True
        if project.get("stack"):
            p.add_run(f" — {project['stack']}")
        for bullet in project.get("bullets", []):
            doc.add_paragraph(bullet, style="List Bullet")

    heading("Education")
    for item in tailored.get("education", []):
        doc.add_paragraph(item, style="List Bullet")

    doc.save(str(path))
    return str(path)
