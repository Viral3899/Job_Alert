"""API Scheduler - calls /api/cron every 15 minutes.

Usage:
    python api_scheduler.py

Can be run alongside api_server.py for local development.
"""

import os
import signal
import sys
import time
from pathlib import Path
from types import FrameType

import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from logging_config import logger

API_URL = os.getenv("API_URL", "http://localhost:8001/api/cron")
CRON_SECRET = os.getenv("CRON_SECRET", "")
INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "15"))

running = True


def signal_handler(signum: int, frame: FrameType | None) -> None:
    global running
    logger.info("Shutdown signal received, stopping scheduler...")
    running = False


def call_cron() -> None:
    """Call the cron endpoint with authentication."""
    headers: dict[str, str] = {}
    if CRON_SECRET:
        headers["Authorization"] = f"Bearer {CRON_SECRET}"

    try:
        response = requests.get(API_URL, headers=headers, timeout=120)
        if response.status_code == 200:
            logger.info("Cron executed successfully: %s", response.text[:200])
        else:
            logger.error("Cron failed: %s - %s", response.status_code, response.text)
    except Exception as exc:
        logger.error("Cron call failed: %s", exc)


def main() -> None:
    global running
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting API Scheduler")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Interval: {INTERVAL_MINUTES} minutes")

    # Run immediately on start
    call_cron()

    while running:
        logger.info(f"Next run in {INTERVAL_MINUTES} minutes...")
        for _ in range(INTERVAL_MINUTES * 60):
            if not running:
                break
            time.sleep(1)
        if running:
            call_cron()

    logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
