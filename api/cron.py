import os
import traceback
from main import process_jobs


def handler(request):
    expected = os.getenv("CRON_SECRET")
    if expected:
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {expected}":
            return {"statusCode": 401, "body": "Unauthorized"}

    try:
        result = process_jobs()
        return {
            "statusCode": 200,
            "body": f"Job monitor executed: {result}",
        }
    except Exception as exc:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": f"Job monitor failed: {exc}",
        }
