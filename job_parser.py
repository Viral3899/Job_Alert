import hashlib
import re
from bs4 import BeautifulSoup

def clean_text(text):
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

def detect_source(sender):
    sender = sender.lower()
    if "linkedin" in sender: return "LinkedIn"
    if "indeed" in sender: return "Indeed"
    if "naukri" in sender: return "Naukri"
    return "Unknown"

def extract_url(text):
    urls = re.findall(r"https?://[^\s<>\"']+", text)
    for url in urls:
        if any(x in url.lower() for x in ("linkedin", "indeed", "naukri")):
            return url
    return urls[0] if urls else ""

def extract_title(subject, body):
    subject = clean_text(subject)
    for pattern in (
        r"job alert.*?:\s*(.*)",
        r"jobs for.*?:\s*(.*)",
        r"new jobs.*?:\s*(.*)",
    ):
        m = re.search(pattern, subject, re.I)
        if m:
            return m.group(1).strip()
    return subject.strip() or "Job Alert"

def extract_company(body):
    for pattern in (
        r"Company[:\s]+([^|\n]+)",
        r"at\s+([A-Z][A-Za-z0-9 .&-]{2,50})",
    ):
        m = re.search(pattern, body, re.I)
        if m:
            return m.group(1).strip()
    return "Unknown"

def extract_location(body):
    locations = ["Remote", "Rajkot",  "Gujarat"]
    lower = body.lower()
    found = [x for x in locations if x.lower() in lower]
    return ", ".join(found) if found else "Unknown"

def parse_email(email):
    body = clean_text(email["body"])
    title = extract_title(email["subject"], body)
    company = extract_company(body)
    location = extract_location(body)
    source = detect_source(email["sender"])
    url = extract_url(email["body"])

    raw = (title.lower() + company.lower() + location.lower() + url.lower())
    job_hash = hashlib.sha256(raw.encode()).hexdigest()

    return {
        "job_hash": job_hash,
        "title": title,
        "company": company,
        "location": location,
        "description": body,
        "source": source,
        "url": url,
        "email_id": email["id"],
    }
