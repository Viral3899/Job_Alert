import sqlite3
from pathlib import Path

DB_PATH = Path("data/jobs.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
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
    """)
    conn.commit()
    return conn

def job_exists(job_hash):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM jobs WHERE job_hash = ? LIMIT 1", (job_hash,)
    ).fetchone()
    conn.close()
    return row is not None

def save_job(job):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO jobs
            (job_hash,title,company,location,description,source,url,
             match_score,matched_skills,email_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            job["job_hash"], job["title"], job["company"], job["location"],
            job["description"], job["source"], job["url"],
            job["match_score"], ", ".join(job["matched_skills"]),
            job["email_id"]
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
