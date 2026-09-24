import time
import traceback

from config import CHECK_INTERVAL_MINUTES, JOB_LOOKBACK_HOURS, MIN_MATCH_SCORE
from database import job_exists, save_job
from gmail_reader import get_job_emails, mark_emails_processed
from job_matcher import match_job
from job_parser import parse_email_jobs
from logging_config import logger
from resume_tailor import build_resume_pdf, tailor_resume
from telegram import send_telegram_document, send_telegram_message


def process_jobs() -> dict:
    logger.info("=" * 60)
    logger.info(f"Checking job alerts from the last {JOB_LOOKBACK_HOURS} hours...")
    logger.info("=" * 60)

    processed_email_ids = []
    try:
        emails = get_job_emails(JOB_LOOKBACK_HOURS)

        for email in emails:
            email_ok = True
            try:
                jobs = parse_email_jobs(email)  # type: ignore[arg-type]
                logger.info(f"Email {email['id']}: {len(jobs)} job(s) detected")

                for raw_job in jobs:
                    try:
                        job = match_job(raw_job)  # type: ignore[arg-type]
                        logger.info(
                            f"  {job['title']} | {job['company']} | "
                            f"{job['match_score']}% | {job['source']} | {job['url']}"
                        )

                        # The exact job URL is the primary deduplication key.
                        if job_exists(job["job_hash"]):
                            logger.info("  Already processed; skipping Telegram.")
                            continue

                        if job["match_score"] >= MIN_MATCH_SCORE:
                            # Generate tailored resume
                            tailored = tailor_resume(job)
                            if tailored:
                                resume_path = build_resume_pdf(job, tailored)
                                logger.info("Tailored resume generated: %s", resume_path)
                                send_telegram_document(job, resume_path)
                            else:
                                logger.warning(
                                    "Failed to generate tailored resume for %s", job.get("title")
                                )
                                # Fallback to just message
                                send_telegram_message(job)
                            logger.info("  Telegram notification sent.")

                        # Save only after the job has been successfully handled.
                        # This prevents a failed Telegram/API operation from being
                        # permanently marked as processed.
                        save_job(job)  # type: ignore[arg-type]

                        if job["match_score"] < MIN_MATCH_SCORE:
                            logger.info(
                                f"  Below {MIN_MATCH_SCORE}% threshold; stored without alert."
                            )

                    except Exception as job_exc:
                        email_ok = False
                        logger.error("Error processing individual job: %s", job_exc)
                        logger.debug(traceback.format_exc())

                # Only label the email after every job in the email was handled.
                if email_ok:
                    processed_email_ids.append(email["id"])

            except Exception as exc:
                logger.error("Error processing email: %s", exc)
                logger.debug(traceback.format_exc())

        # Gmail label is the cross-run/serverless deduplication layer.
        if processed_email_ids:
            mark_emails_processed(processed_email_ids)

        logger.info("Processed %d emails", len(processed_email_ids))
        return {"emails": len(emails), "processed_emails": len(processed_email_ids)}

    except Exception as exc:
        logger.critical("Main error: %s", exc)
        logger.debug(traceback.format_exc())
        raise


def main() -> None:
    logger.info("Job Monitor Started")
    logger.info(f"Checking every {CHECK_INTERVAL_MINUTES} minutes.")
    logger.info(f"Job lookback: {JOB_LOOKBACK_HOURS} hours")
    logger.info(f"Minimum match: {MIN_MATCH_SCORE}%")

    while True:
        process_jobs()
        logger.info(f"Next check in {CHECK_INTERVAL_MINUTES} minutes...")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
