import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(job):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return

    skills = ", ".join(job["matched_skills"]) or "No specific skill detected"

    message = (
        "🚨 NEW JOB MATCH\n\n"
        f"💼 {job['title']}\n"
        f"🏢 {job['company']}\n"
        f"📍 {job['location']}\n"
        f"🔥 Match Score: {job['match_score']}%\n\n"
        f"🧠 Matched Skills:\n{skills}\n\n"
        f"🌐 Source: {job['source']}\n\n"
        f"🔗 Apply:\n{job['url']}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=20
    )
    response.raise_for_status()
