import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def _api(method):
    token = (TELEGRAM_BOT_TOKEN or "").strip()
    return f"https://api.telegram.org/bot{token}/{method}"


def send_telegram_message(job):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return False
    if "=" in TELEGRAM_BOT_TOKEN or not TELEGRAM_BOT_TOKEN.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Invalid TELEGRAM_BOT_TOKEN format. Set only the token value, not TELEGRAM_BOT_TOKEN=...")

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
    return True
