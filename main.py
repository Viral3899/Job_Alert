import time
import traceback

from config import CHECK_INTERVAL_MINUTES, JOB_LOOKBACK_HOURS, MIN_MATCH_SCORE
from gmail_reader import get_job_emails, mark_emails_processed
from job_parser import parse_email_jobs
from job_matcher import match_job
from database import job_exists, save_job
from telegram import send_telegram_message


def process_jobs():
    print("\n" + "=" * 60)
    print(f"Checking job alerts from the last {JOB_LOOKBACK_HOURS} hours...")
    print("=" * 60)

    processed_email_ids = []
    try:
        emails = get_job_emails(JOB_LOOKBACK_HOURS)

        for email in emails:
            email_ok = True
            try:
                jobs = parse_email_jobs(email)
                print(f"Email {email['id']}: {len(jobs)} job(s) detected")

                for raw_job in jobs:
                    try:
                        job = match_job(raw_job)
                        print(
                            f"  {job['title']} | {job['company']} | "
                            f"{job['match_score']}% | {job['source']} | {job['url']}"
                        )

                        # The exact job URL is the primary deduplication key.
                        if job_exists(job["job_hash"]):
                            print("  Already processed; skipping Telegram.")
                            continue

                        if job["match_score"] >= MIN_MATCH_SCORE:
                            # Job alerts only: no resume generation, no Groq calls.
                            send_telegram_message(job)
                            print("  Telegram notification sent.")

                        # Save only after the job has been successfully handled.
                        # This prevents a failed Telegram/API operation from being
                        # permanently marked as processed.
                        save_job(job)

                        if job["match_score"] < MIN_MATCH_SCORE:
                            print(f"  Below {MIN_MATCH_SCORE}% threshold; stored without alert.")

                    except Exception as job_exc:
                        email_ok = False
                        print("Error processing individual job:", job_exc)
                        traceback.print_exc()

                # Only label the email after every job in the email was handled.
                if email_ok:
                    processed_email_ids.append(email["id"])

            except Exception as exc:
                print("Error processing email:", exc)
                traceback.print_exc()

        # Gmail label is the cross-run/serverless deduplication layer.
        if processed_email_ids:
            mark_emails_processed(processed_email_ids)

        return {"emails": len(emails), "processed_emails": len(processed_email_ids)}

    except Exception as exc:
        print("Main error:", exc)
        traceback.print_exc()
        raise


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
