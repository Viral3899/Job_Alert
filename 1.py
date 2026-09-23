import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN is missing in .env")
    exit(1)

if not CHAT_ID:
    print("❌ TELEGRAM_CHAT_ID is missing in .env")
    exit(1)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": (
        "🚀 Job Monitor Test\n\n"
        "✅ Telegram bot is connected successfully!\n"
        "🔔 You will receive matching job alerts here."
    )
}

try:
    response = requests.post(
        url,
        data=payload,
        timeout=20
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.json())

    if response.ok:
        print("\n✅ SUCCESS! Check your Telegram.")
    else:
        print("\n❌ Telegram API returned an error.")

except Exception as e:
    print("\n❌ Connection error:")
    print(e)