from pathlib import Path

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from logging_config import logger


def _api(method: str) -> str:
    token = (TELEGRAM_BOT_TOKEN or "").strip()
    return f"https://api.telegram.org/bot{token}/{method}"


def send_telegram_message(job: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials are missing.")
        return False
    if (
        "=" in TELEGRAM_BOT_TOKEN
        or not TELEGRAM_BOT_TOKEN.replace("_", "").replace("-", "").isalnum()
    ):
        raise ValueError(
            "Invalid TELEGRAM_BOT_TOKEN format. Set only the token value, not TELEGRAM_BOT_TOKEN=..."
        )

    skills = ", ".join(job.get("matched_skills", [])) or "No specific skill detected"
    url = job.get("url") or ""
    message = (
        "🚨 NEW JOB MATCH\n\n"
        f"💼 {job.get('title', 'Unknown')}\n"
        f"🏢 {job.get('company', 'Unknown')}\n"
        f"📍 {job.get('location', 'Unknown')}\n"
        f"🔥 Match Score: {job.get('match_score', 0)}%\n"
        f"🌐 Source: {job.get('source', 'Unknown')}\n\n"
        f"🧠 Skills: {skills}\n\n"
        f"🔗 Apply: {url}\n\n"
        "⏱️ Alert window: last 48 hours"
    )
    response = requests.post(
        _api("sendMessage"),
        data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": "false"},
        timeout=20,
    )
    response.raise_for_status()
    logger.info("Telegram notification sent for job: %s", job.get("title", "Unknown"))
    return True


def send_telegram_document(job: dict, file_path: str, caption: str | None = None) -> bool:
    """Send a DOCX file to Telegram with optional caption."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials are missing.")
        return False

    default_caption = (
        f"📄 Tailored Resume\n\n"
        f"💼 {job.get('title', 'Unknown')}\n"
        f"🏢 {job.get('company', 'Unknown')}\n"
        f"🔥 Match Score: {job.get('match_score', 0)}%\n"
        f"🔗 Apply: {job.get('url', '')}"
    )
    caption = caption or default_caption

    try:
        with open(file_path, "rb") as doc:
            files = {
                "document": (
                    Path(file_path).name,
                    doc,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            }
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = requests.post(_api("sendDocument"), data=data, files=files, timeout=60)
            response.raise_for_status()
        logger.info("Telegram document sent for job: %s", job.get("title", "Unknown"))
        return True
    except Exception as exc:
        logger.error("Failed to send Telegram document: %s", exc)
        return False
