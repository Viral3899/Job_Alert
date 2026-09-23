import os
from main import process_jobs


def handler(request):
    expected = os.getenv("CRON_SECRET")
    if expected:
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {expected}":
            return {"statusCode": 401, "body": "Unauthorized"}
    process_jobs()
    return {"statusCode": 200, "body": "Job monitor executed"}
