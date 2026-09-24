import hashlib
import sqlite3
from pathlib import Path
from typing import Any, TypedDict

DB_PATH = Path("data/jobs.db")


class JobDict(TypedDict):
    job_hash: str
    title: str
    company: str
    location: str
    description: str
    source: str
    url: str
    match_score: int
    matched_skills: list[str]
    email_id: str


def _canonical_key(job: dict[str, Any]) -> str:
    """Prefer the exact job URL for deduplication; fall back to job metadata."""
    url = (job.get("url") or "").strip().lower()
    if url and not url.endswith("/"):
        return f"url:{url}"
    raw = (
        "|".join(
            [
                job.get("source", ""),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
            ]
        )
        .strip()
        .lower()
    )
    return f"meta:{raw}"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_hash TEXT UNIQUE,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            source TEXT,
            url TEXT,
            match_score INTEGER,
            matched_skills TEXT,
            email_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    return conn


def job_hash_for(job: dict[str, Any]) -> str:
    key = _canonical_key(job)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def job_exists(job_hash: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM jobs WHERE job_hash = ? LIMIT 1", (job_hash,)).fetchone()
    conn.close()
    return row is not None


def save_job(job: dict[str, Any]) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO jobs
            (job_hash,title,company,location,description,source,url,
             match_score,matched_skills,email_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
            (
                job["job_hash"],
                job["title"],
                job["company"],
                job["location"],
                job["description"],
                job["source"],
                job["url"],
                job["match_score"],
                ", ".join(job["matched_skills"]),
                job["email_id"],
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
