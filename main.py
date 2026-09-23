import time
import traceback

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config import CHECK_INTERVAL_MINUTES, MIN_MATCH_SCORE
from gmail_reader import get_job_emails
from job_parser import parse_email
from job_matcher import match_job
from database import job_exists, save_job
from telegram import send_telegram_message

app = FastAPI(
    title="Job Alert API",
    description="Fetches the latest job-alert emails from Gmail and matches them to an AI/ML profile.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Job Alert API",
        "endpoints": {
            "health": "/health",
            "latest_jobs": "/jobs/latest",
            "api_latest_jobs": "/api/jobs",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "job-alert"}


def fetch_latest_jobs(limit: int = 50):
    emails = get_job_emails(hours=24, max_results=limit)
    jobs = []

    for email in emails:
        try:
            job = match_job(parse_email(email))
            job["received_at"] = email.get("received_at", "")
            jobs.append(job)
        except Exception as exc:
            print(f"Error parsing email {email.get('id')}: {exc}")

    jobs.sort(key=lambda item: item.get("received_at", ""), reverse=True)
    return jobs[:limit]


@app.get("/jobs/latest")
def latest_jobs(
    limit: int = Query(50, ge=1, le=100),
    min_score: int = Query(0, ge=0, le=100),
):
    """Return jobs received in the latest 24-hour Gmail window."""
    try:
        jobs = fetch_latest_jobs(limit=limit)
        if min_score:
            jobs = [job for job in jobs if job["match_score"] >= min_score]

        return {
            "success": True,
            "window": "last_24_hours",
            "count": len(jobs),
            "jobs": jobs,
        }
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/jobs")
def api_latest_jobs(
    limit: int = Query(50, ge=1, le=100),
    min_score: int = Query(0, ge=0, le=100),
):
    return latest_jobs(limit=limit, min_score=min_score)


def process_jobs():
    print("\n" + "=" * 60)
    print("Checking job alerts from the last 24 hours...")
    print("=" * 60)

    try:
        emails = get_job_emails(hours=24, max_results=100)
        print(f"Found {len(emails)} job-alert emails from the last 24 hours.")

        for email in emails:
            try:
                job = match_job(parse_email(email))

                print(
                    f"\n{job['title']} | {job['company']} | "
                    f"{job['match_score']}%"
                )

                if job_exists(job["job_hash"]):
                    print("Already processed.")
                    continue

                save_job(job)

                if job["match_score"] >= MIN_MATCH_SCORE:
                    send_telegram_message(job)
                    print("Telegram notification sent.")
                else:
                    print("Below match threshold.")

            except Exception as exc:
                print("Error processing email:", exc)

    except Exception as exc:
        print("Main error:", exc)
        traceback.print_exc()


def main():
    print("🚀 Job Monitor Started")
    print(f"Checking every {CHECK_INTERVAL_MINUTES} minutes.")
    print("Each check only fetches job alerts from the last 24 hours.")

    while True:
        process_jobs()
        print(f"\nNext check in {CHECK_INTERVAL_MINUTES} minutes...")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
