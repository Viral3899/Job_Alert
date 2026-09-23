import os
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def _api(method):
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"


def send_telegram_message(job, resume_path=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return False

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
        "📄 Tailored resume: attached\n"
        "⏱️ Alert window: last 48 hours"
    )
    response = requests.post(
        _api("sendMessage"),
        data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": "false"},
        timeout=20,
    )
    response.raise_for_status()

    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as fh:
            doc_response = requests.post(
                _api("sendDocument"),
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": "📄 Tailored ATS resume for this job"},
                files={"document": (os.path.basename(resume_path), fh, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                timeout=60,
            )
        doc_response.raise_for_status()
    return True
