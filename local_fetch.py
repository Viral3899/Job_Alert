"""Local job fetcher - runs once, fetches latest 50 jobs, sends 60%+ matches to Telegram.

Usage:
    python local_fetch.py

Can be scheduled via Windows Task Scheduler or cron to run every 15 minutes.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import MIN_MATCH_SCORE
from database import job_exists, save_job
from gmail_reader import get_job_emails
from job_matcher import match_job
from job_parser import parse_email_jobs
from logging_config import logger
from resume_tailor import build_resume_pdf, tailor_resume
from telegram import send_telegram_document, send_telegram_message


def fetch_and_notify(lookback_hours: int = 48, max_jobs: int = 50, min_match: int = 60) -> dict:
    """Fetch jobs from Gmail and send notifications for matches >= min_match."""
    logger.info("=" * 60)
    logger.info(f"Local fetch: last {lookback_hours}h, max {max_jobs} jobs, min {min_match}% match")
    logger.info("=" * 60)

    emails = get_job_emails(lookback_hours)
    logger.info(f"Found {len(emails)} unprocessed job-alert email(s)")

    jobs_processed = 0
    jobs_notified = 0

    for email in emails:
        try:
            jobs = parse_email_jobs(email)  # type: ignore[arg-type]
            logger.info(f"Email {email['id']}: {len(jobs)} job(s) detected")

            for raw_job in jobs:
                if jobs_processed >= max_jobs:
                    logger.info(f"Reached max jobs limit ({max_jobs}), stopping")
                    return {
                        "emails_processed": len(emails),
                        "jobs_processed": jobs_processed,
                        "jobs_notified": jobs_notified,
                    }

                try:
                    job = match_job(raw_job)  # type: ignore[arg-type]
                    logger.info(
                        f"  {job['title']} | {job['company']} | "
                        f"{job['match_score']}% | {job['source']} | {job['url']}"
                    )

                    jobs_processed += 1

                    # Skip if already processed
                    if job_exists(job["job_hash"]):
                        logger.info("  Already processed; skipping")
                        continue

                    # Only notify if match >= threshold
                    if job["match_score"] >= min_match:
                        tailored = tailor_resume(job)
                        if tailored:
                            resume_path = build_resume_pdf(job, tailored)
                            logger.info("Tailored resume generated: %s", resume_path)
                            send_telegram_document(job, resume_path)
                        else:
                            logger.warning(
                                "Failed to generate tailored resume for %s", job.get("title")
                            )
                            send_telegram_message(job)
                        jobs_notified += 1
                        logger.info("  Telegram notification sent.")
                    else:
                        logger.info(f"  Below {min_match}% threshold; stored without alert.")

                    # Save after successful handling
                    save_job(job)

                except Exception as job_exc:
                    logger.error("Error processing individual job: %s", job_exc)

        except Exception as exc:
            logger.error("Error processing email: %s", exc)

    logger.info("Done: %d jobs processed, %d notifications sent", jobs_processed, jobs_notified)
    return {
        "emails_processed": len(emails),
        "jobs_processed": jobs_processed,
        "jobs_notified": jobs_notified,
    }


def main() -> None:
    # Allow overriding via env vars
    lookback_hours = int(os.getenv("LOCAL_LOOKBACK_HOURS", "48"))
    max_jobs = int(os.getenv("LOCAL_MAX_JOBS", "50"))
    min_match = int(os.getenv("LOCAL_MIN_MATCH", str(MIN_MATCH_SCORE)))

    logger.info("Starting local job fetch...")
    result = fetch_and_notify(
        lookback_hours=lookback_hours,
        max_jobs=max_jobs,
        min_match=min_match,
    )
    logger.info("Result: %s", result)


if __name__ == "__main__":
    main()
