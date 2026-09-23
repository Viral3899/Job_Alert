import time
import traceback

from config import CHECK_INTERVAL_MINUTES, MIN_MATCH_SCORE
from gmail_reader import get_job_emails
from job_parser import parse_email
from job_matcher import match_job
from database import job_exists, save_job
from telegram import send_telegram_message

def process_jobs():
    print("\n" + "=" * 60)
    print("Checking job alerts...")
    print("=" * 60)

    try:
        emails = get_job_emails()
        print(f"Found {len(emails)} job-alert emails.")

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

    while True:
        process_jobs()
        print(f"\nNext check in {CHECK_INTERVAL_MINUTES} minutes...")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
