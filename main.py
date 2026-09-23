import time
import traceback

from config import CHECK_INTERVAL_MINUTES, JOB_LOOKBACK_HOURS, MIN_MATCH_SCORE
from gmail_reader import get_job_emails, mark_emails_processed
from job_parser import parse_email_jobs
from job_matcher import match_job
from database import job_exists, save_job
from telegram import send_telegram_message
from resume_tailor import tailor_resume, build_resume_docx


def process_jobs():
    print("\n" + "=" * 60)
    print(f"Checking job alerts from the last {JOB_LOOKBACK_HOURS} hours...")
    print("=" * 60)

    try:
        emails = get_job_emails(JOB_LOOKBACK_HOURS)
        processed_email_ids = []

        for email in emails:
            try:
                jobs = parse_email_jobs(email)
                print(f"Email {email['id']}: {len(jobs)} job(s) detected")

                for raw_job in jobs:
                    job = match_job(raw_job)
                    print(
                        f"  {job['title']} | {job['company']} | "
                        f"{job['match_score']}% | {job['source']}"
                    )

                    if job_exists(job["job_hash"]):
                        print("  Already processed.")
                        continue

                    save_job(job)
                    if job["match_score"] >= MIN_MATCH_SCORE:
                        tailored = tailor_resume(job)
                        resume_path = build_resume_docx(job, tailored) if tailored else None
                        send_telegram_message(job, resume_path)
                        print("  Telegram notification + tailored resume sent.")
                    else:
                        print(f"  Below {MIN_MATCH_SCORE}% threshold.")

                # Mark the source email only after all jobs in it have been handled.
                processed_email_ids.append(email["id"])

            except Exception as exc:
                print("Error processing email:", exc)
                traceback.print_exc()

        # Gmail label provides persistent deduplication across local runs and Vercel.
        if processed_email_ids:
            mark_emails_processed(processed_email_ids)

    except Exception as exc:
        print("Main error:", exc)
        traceback.print_exc()


def main():
    print("🚀 Job Monitor Started")
    print(f"Checking every {CHECK_INTERVAL_MINUTES} minutes.")
    print(f"Job lookback: {JOB_LOOKBACK_HOURS} hours")
    print(f"Minimum match: {MIN_MATCH_SCORE}%")

    while True:
        process_jobs()
        print(f"\nNext check in {CHECK_INTERVAL_MINUTES} minutes...")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
