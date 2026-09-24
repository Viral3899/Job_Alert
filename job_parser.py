import hashlib
import re
from html import unescape
from typing import Any, TypedDict
from urllib.parse import ParseResult, parse_qs, unquote, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

TRACKING_KEYS: set[str] = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_name",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "trk",
    "trkemail",
    "src",
    "sid",
    "xp",
    "px",
    "nignbevent_src",
    "ref",
    "refid",
}


class JobDict(TypedDict):
    job_hash: str
    title: str
    company: str
    location: str
    description: str
    source: str
    url: str
    email_id: str
    email_date: str
    internal_date: int


def clean_text(text: str | None) -> str:
    return str(BeautifulSoup(text or "", "html.parser").get_text(" ", strip=True))


def detect_source(sender: str, text: str = "") -> str:
    value = f"{sender} {text}".lower()
    checks = [
        ("linkedin", "LinkedIn"),
        ("indeed", "Indeed"),
        ("naukri", "Naukri"),
        ("wellfound", "Wellfound"),
        ("angel.co", "Wellfound"),
        ("cutshort", "Cutshort"),
        ("instahyre", "Instahyre"),
        ("hirist", "Hirist"),
        ("foundit", "Foundit"),
        ("monster", "Foundit"),
        ("timesjobs", "TimesJobs"),
        ("shine", "Shine"),
        ("freshersworld", "Freshersworld"),
    ]
    for needle, source in checks:
        if needle in value:
            return source
    return "Unknown"


def _unwrap_tracking_url(url: str | None, max_depth: int = 5) -> str:
    url = unescape(unquote(url or "")).strip().strip("<>\"'")
    for _ in range(max_depth):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        candidate: str | None = None
        for key in (
            "url",
            "u",
            "redirect",
            "redirect_url",
            "dest",
            "destination",
            "target",
            "link",
            "continue",
            "return",
            "redirectUrl",
        ):
            if params.get(key):
                candidate = params[key][0]
                break
        # Handle Indeed's /f/a/ tracking URLs (engage.indeed.com/f/a/...)
        if not candidate and "engage.indeed.com" in parsed.netloc and "/f/a/" in parsed.path:
            # These are opaque tracking URLs that redirect to viewjob?jk=...
            # We can't extract jk without following redirect, so return as-is
            # The normalize_job_url will handle it
            pass
        if not candidate:
            break
        candidate = unescape(unquote(candidate))
        if candidate.startswith(("http://", "https://")):
            url = candidate
        else:
            break
    return url


def _clean_query(parsed: ParseResult) -> str:
    allowed: list[tuple[str, str]] = []
    for key, values in parse_qs(parsed.query, keep_blank_values=True).items():
        if key.lower() in TRACKING_KEYS:
            continue
        for value in values:
            allowed.append((key, value))
    return urlencode(allowed)


def _fallback_search_url(source: str, title: str = "") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    if source == "Naukri":
        return f"https://www.naukri.com/{slug}-jobs" if slug else "https://www.naukri.com/"
    if source == "LinkedIn":
        return "https://www.linkedin.com/jobs/"
    if source == "Indeed":
        return "https://in.indeed.com/"
    if source == "Wellfound":
        return "https://wellfound.com/jobs"
    return ""


def normalize_job_url(
    url: str | None, source: str, title: str = "", company: str = "", location: str = ""
) -> str:
    if not url:
        return _fallback_search_url(source, title)

    url = _unwrap_tracking_url(url)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return _fallback_search_url(source, title)

    host = parsed.netloc.lower().replace("www.", "")
    path = parsed.path or "/"
    query = _clean_query(parsed)

    if source == "Naukri":
        if "naukri.com" in host and "/job-listings-" in path.lower():
            return urlunparse(("https", "www.naukri.com", path, "", query, ""))
        return _fallback_search_url(source, title)

    if source == "LinkedIn":
        if "linkedin.com" in host:
            match = re.search(r"/jobs/view/(\d+)", path, re.I)
            if match:
                return f"https://www.linkedin.com/jobs/view/{match.group(1)}/"
            # Some alerts use a company/job path rather than a numeric job view.
            if "/jobs/" in path.lower() and "/jobs/view/" not in path.lower():
                return urlunparse(("https", "www.linkedin.com", path, "", query, ""))
        return _fallback_search_url(source, title)

    if source == "Indeed":
        if "indeed." in host:
            # Convert Indeed redirect links into the canonical job-specific viewjob URL.
            jk_values = parse_qs(parsed.query).get("jk", [])
            if jk_values and jk_values[0]:
                return f"https://{parsed.netloc}/viewjob?jk={jk_values[0]}"
            match = re.search(r"[?&]jk=([A-Za-z0-9_-]+)", url, re.I)
            if match:
                return f"https://{parsed.netloc}/viewjob?jk={match.group(1)}"
            if "viewjob" in path.lower():
                return urlunparse(("https", parsed.netloc, path, "", query, ""))
            # Handle Indeed's /f/a/ tracking URLs (engage.indeed.com/f/a/...)
            # These are opaque tracking URLs that redirect to the actual job.
            # Since we can't extract jk without following redirect, fall back to search URL.
            if "engage.indeed.com" in host and "/f/a/" in path:
                return _fallback_search_url(source, title)
            return urlunparse(("https", parsed.netloc, path, "", query, ""))

    # Other platforms: preserve the actual URL after removing tracking parameters.
    return urlunparse(("https", parsed.netloc, path, "", query, ""))


def _is_platform_link(href: str, anchor_text: str, source: str) -> bool:
    value = f"{href} {anchor_text}".lower()
    domains = {
        "LinkedIn": "linkedin",
        "Indeed": "indeed",
        "Naukri": "naukri",
        "Wellfound": "wellfound",
        "Cutshort": "cutshort",
        "Instahyre": "instahyre",
        "Hirist": "hirist",
        "Foundit": "foundit",
        "TimesJobs": "timesjobs",
        "Shine": "shine",
        "Freshersworld": "freshersworld",
    }
    needle = domains.get(source)
    return bool(needle and needle in value)


def _extract_links(raw_html: str | None, source: str) -> list[tuple[str, str, BeautifulSoup]]:
    soup = BeautifulSoup(raw_html or "", "html.parser")
    links: list[tuple[str, str, BeautifulSoup]] = []
    for a in soup.find_all("a", href=True):
        href = unescape(a.get("href", "")).strip()
        if not href.startswith(("http://", "https://")):
            continue
        text = clean_text(a.get_text(" ", strip=True))
        if not _is_platform_link(href, text, source):
            continue
        links.append((href, text, a))
    return links


def _title_from_anchor(anchor_text: str, subject: str) -> str:
    text = clean_text(anchor_text)
    # Avoid treating generic CTA labels as the job title.
    generic = {
        "apply now",
        "view job",
        "apply",
        "see job",
        "view job details",
        "learn more",
        "open job",
    }
    if len(text) >= 4 and len(text) <= 180 and text.lower() not in generic:
        return text
    subject = clean_text(subject)
    for pattern in (r"job alert.*?:\s*(.*)", r"jobs for.*?:\s*(.*)", r"new jobs.*?:\s*(.*)"):
        m = re.search(pattern, subject, re.I)
        if m:
            return m.group(1).strip()
    return subject or "Job Alert"


def _title_from_anchor_element(anchor: BeautifulSoup | None, anchor_text: str, subject: str) -> str:
    generic = {
        "apply now",
        "view job",
        "apply",
        "see job",
        "view job details",
        "learn more",
        "open job",
    }
    if anchor is not None and clean_text(anchor.get_text(" ", strip=True)).lower() in generic:
        heading = anchor.find_previous(["h1", "h2", "h3", "h4", "h5", "strong"])
        if heading:
            value = clean_text(heading.get_text(" ", strip=True))
            if 4 <= len(value) <= 180:
                return value
        # For Indeed: look for job title in nearby elements
        if anchor:
            # Check parent and siblings for job title
            parent = anchor.parent
            if parent:
                # Look for heading-like elements in parent
                for tag in parent.find_all(
                    ["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b", "span"]
                ):
                    value = clean_text(tag.get_text(" ", strip=True))
                    if 4 <= len(value) <= 180 and value.lower() not in generic:
                        return value
    return _title_from_anchor(anchor_text, subject)


def _context_text(anchor: BeautifulSoup | None) -> str:
    """Get text from the closest card/table/list container around one job link."""
    if not anchor:
        return ""
    node = anchor
    for _ in range(5):
        node = node.parent
        if not node:
            break
        text = clean_text(str(node))
        if 30 <= len(text) <= 2500:
            return text
    return clean_text(anchor.parent.get_text(" ", strip=True)) if anchor.parent else ""


def extract_company(text: str | None) -> str:
    for pattern in (
        r"Company[:\s]+([^|\n]+)",
        r"Employer[:\s]+([^|\n]+)",
        r"(?:company|employer)\s*[-:]\s*([^|\n]+)",
        r"at\s+([A-Z][A-Za-z0-9 .&'()-]{2,80})",
        # Indeed-specific patterns
        r"([A-Z][A-Za-z0-9 .&'()-]{2,80})\s*[-–]\s*(?:Remote|Hybrid|On-site)",
        r"([A-Z][A-Za-z0-9 .&'()-]{2,80})\s*\|\s*(?:Remote|Hybrid|On-site)",
    ):
        m = re.search(pattern, text or "", re.I)
        if m:
            value = m.group(1).strip(" -|:")
            if value and len(value) < 100:
                return value
    return "Unknown"


def extract_location(text: str | None) -> str:
    candidates = [
        "Remote",
        "Remote India",
        "Rajkot",
        "Ahmedabad",
        "Gandhinagar",
        "GIFT City",
        "Gujarat",
        "Bengaluru",
        "Bangalore",
        "Hyderabad",
        "Pune",
        "Gurugram",
        "Gurgaon",
        "Noida",
        "Delhi",
        "Mumbai",
        "Chennai",
        "Indore",
        "India",
    ]
    lower = (text or "").lower()
    found = [x for x in candidates if x.lower() in lower]
    return ", ".join(dict.fromkeys(found)) if found else "Unknown"


def _build_job(
    email: dict, title: str, company: str, location: str, source: str, url: str, description: str
) -> JobDict:
    url = normalize_job_url(url, source, title, company, location)
    # URL is the primary identity whenever it is an exact job URL.
    identity = (
        url.lower().rstrip("/")
        if url
        else "|".join([source.lower(), title.lower(), company.lower(), location.lower()])
    )
    job_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return {
        "job_hash": job_hash,
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


def parse_email(email: dict) -> JobDict:
    jobs = parse_email_jobs(email)
    return (
        jobs[0]
        if jobs
        else _build_job(
            email,
            clean_text(email.get("subject", "")),
            "Unknown",
            "Unknown",
            detect_source(email.get("sender", ""), email.get("body", "")),
            "",
            clean_text(email.get("body", "")),
        )
    )


def parse_email_jobs(email: dict[str, Any]) -> list[JobDict]:
    """Extract every job card and preserve its own apply URL and local card text."""
    raw = email.get("raw_html") or email.get("body", "")
    body = clean_text(email.get("body", ""))
    source = detect_source(email.get("sender", ""), raw)
    links = _extract_links(raw, source)

    jobs: list[JobDict] = []
    seen: set[str] = set()
    for href, anchor_text, anchor in links:
        context = _context_text(anchor) or body
        title = _title_from_anchor_element(anchor, anchor_text, email.get("subject", ""))
        normalized = normalize_job_url(href, source, title)

        # If normalization returned only a generic platform page, do not use it
        # as a unique job identity when we have no exact job URL.
        exact = any(
            marker in normalized.lower()
            for marker in ("/jobs/view/", "/job-listings-", "viewjob", "/jobs/", "/job/")
        )
        if not exact and source in {"LinkedIn", "Naukri"}:
            continue

        key = (
            normalized.lower().rstrip("/")
            if normalized
            else f"{title.lower()}|{context.lower()[:300]}"
        )
        if key in seen:
            continue
        seen.add(key)

        company = extract_company(context)
        location = extract_location(context)
        description = context if len(context) >= 80 else body
        jobs.append(_build_job(email, title, company, location, source, normalized, description))

    # Fallback: some plain-text alerts do not expose usable HTML links.
    if not jobs:
        title = _title_from_anchor("", email.get("subject", ""))
        jobs.append(
            _build_job(
                email,
                title,
                extract_company(body),
                extract_location(body),
                source,
                normalize_job_url("", source, title),
                body,
            )
        )

    return jobs
