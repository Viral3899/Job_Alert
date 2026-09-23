import hashlib
import re
from html import unescape
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse, urlunparse
from bs4 import BeautifulSoup


def clean_text(text):
    return BeautifulSoup(text or "", "html.parser").get_text(" ", strip=True)


def detect_source(sender, text=""):
    value = f"{sender} {text}".lower()
    if "linkedin" in value:
        return "LinkedIn"
    if "indeed" in value:
        return "Indeed"
    if "naukri" in value:
        return "Naukri"
    if "wellfound" in value or "angel.co" in value:
        return "Wellfound"
    if "cutshort" in value:
        return "Cutshort"
    if "instahyre" in value:
        return "Instahyre"
    if "hirist" in value:
        return "Hirist"
    if "foundit" in value or "monster" in value:
        return "Foundit"
    if "timesjobs" in value:
        return "TimesJobs"
    if "shine" in value:
        return "Shine"
    if "freshersworld" in value:
        return "Freshersworld"
    return "Unknown"


def _unwrap_tracking_url(url, max_depth=3):
    url = unescape(unquote(url)).strip().strip("<>\"'")
    for _ in range(max_depth):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        candidate = None
        for key in ("url", "u", "redirect", "redirect_url", "dest", "destination", "target", "link"):
            if params.get(key):
                candidate = params[key][0]
                break
        if not candidate:
            break
        candidate = unescape(unquote(candidate))
        if candidate.startswith("http"):
            url = candidate
        else:
            break
    return url


def normalize_job_url(url, source, title="", company="", location=""):
    if not url:
        return ""
    url = _unwrap_tracking_url(url)
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")

    # Strip tracking parameters while keeping the canonical path/query.
    allowed = []
    for k, values in parse_qs(parsed.query, keep_blank_values=True).items():
        if k.lower() in {"src", "sid", "xp", "px", "nignbevent_src", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}:
            continue
        for v in values:
            allowed.append((k, v))
    query = urlencode(allowed)
    canonical = urlunparse(("https", parsed.netloc, parsed.path, "", query, ""))

    if source == "Naukri":
        if "naukri.com" in host and "/job-listings-" in parsed.path.lower():
            return canonical
        # If email contains a generic Naukri URL, provide a working search URL
        # rather than sending a broken tracking URL to Telegram.
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if slug:
            return f"https://www.naukri.com/{slug}-jobs"
        return "https://www.naukri.com/"

    return canonical


def _extract_links(raw_html, source):
    soup = BeautifulSoup(raw_html or "", "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = unescape(a.get("href", "")).strip()
        if not href.startswith("http"):
            continue
        text = clean_text(a.get_text(" ", strip=True))
        if source == "Naukri" and "naukri" not in href.lower() and "naukri" not in text.lower():
            continue
        if source == "LinkedIn" and "linkedin" not in href.lower() and "linkedin" not in text.lower():
            continue
        if source == "Indeed" and "indeed" not in href.lower() and "indeed" not in text.lower():
            continue
        links.append((href, text))
    return links


def _title_from_anchor(anchor_text, subject):
    text = clean_text(anchor_text)
    if len(text) >= 4 and len(text) <= 180:
        return text
    subject = clean_text(subject)
    for pattern in (r"job alert.*?:\s*(.*)", r"jobs for.*?:\s*(.*)", r"new jobs.*?:\s*(.*)"):
        m = re.search(pattern, subject, re.I)
        if m:
            return m.group(1).strip()
    return subject or "Job Alert"


def extract_company(text):
    for pattern in (
        r"Company[:\s]+([^|\n]+)",
        r"Employer[:\s]+([^|\n]+)",
        r"at\s+([A-Z][A-Za-z0-9 .&-]{2,60})",
    ):
        m = re.search(pattern, text, re.I)
        if m:
            value = m.group(1).strip(" -|:")
            if value:
                return value
    return "Unknown"


def extract_location(text):
    candidates = [
        "Remote", "Rajkot", "Ahmedabad", "Gandhinagar", "GIFT City", "Gujarat",
        "Bengaluru", "Bangalore", "Hyderabad", "Pune", "Gurugram", "Gurgaon",
        "Noida", "Delhi", "Mumbai", "Chennai", "Indore", "India",
    ]
    lower = text.lower()
    found = [x for x in candidates if x.lower() in lower]
    return ", ".join(dict.fromkeys(found)) if found else "Unknown"


def _build_job(email, title, company, location, source, url, description):
    url = normalize_job_url(url, source, title, company, location)
    raw = (title.lower() + company.lower() + location.lower() + url.lower())
    return {
        "job_hash": hashlib.sha256(raw.encode()).hexdigest(),
        "title": title.strip() or "Job Alert",
        "company": company.strip() or "Unknown",
        "location": location.strip() or "Unknown",
        "description": description,
        "source": source,
        "url": url,
        "email_id": email["id"],
        "email_date": email.get("date", ""),
        "internal_date": email.get("internal_date", 0),
    }


def parse_email(email):
    raw = email.get("body", "")
    body = clean_text(raw)
    source = detect_source(email.get("sender", ""), raw)
    links = _extract_links(raw, source)

    # Prefer actual job links. If several are present, use the first one for the
    # legacy single-job path; parse_email_jobs() below handles all of them.
    job_links = []
    for href, anchor_text in links:
        normalized = normalize_job_url(href, source, anchor_text)
        if source == "Naukri" and "/job-listings-" not in normalized.lower():
            continue
        job_links.append((normalized, anchor_text))

    title = _title_from_anchor(job_links[0][1] if job_links else "", email.get("subject", ""))
    company = extract_company(body)
    location = extract_location(body)
    url = job_links[0][0] if job_links else normalize_job_url("", source, title, company, location)
    return _build_job(email, title, company, location, source, url, body)


def parse_email_jobs(email):
    """Parse one email into one or more jobs when the alert contains multiple cards."""
    raw = email.get("body", "")
    body = clean_text(raw)
    source = detect_source(email.get("sender", ""), raw)
    links = _extract_links(raw, source)

    seen = set()
    jobs = []
    for href, anchor_text in links:
        normalized = normalize_job_url(href, source, anchor_text)
        if source == "Naukri" and "/job-listings-" not in normalized.lower():
            continue
        if source == "LinkedIn" and "/jobs/view/" not in normalized.lower():
            continue
        if source == "Indeed" and "indeed" not in normalized.lower():
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)

        title = _title_from_anchor(anchor_text, email.get("subject", ""))
        # Use text around the anchor when possible for company/location clues.
        company = extract_company(body)
        location = extract_location(body)
        job = _build_job(email, title, company, location, source, normalized, body)
        jobs.append(job)

    if not jobs:
        jobs.append(parse_email(email))

    return jobs
