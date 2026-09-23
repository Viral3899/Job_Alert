import base64
import json
import os
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _json_from_env(name):
    value = os.getenv(name)
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{name} must contain valid JSON.") from exc


def get_gmail_service():
    """
    Local: credentials.json + token.json.
    Vercel: GMAIL_TOKEN_JSON (+ GMAIL_CREDENTIALS_JSON when needed).
    """
    creds = None
    token_from_env = bool(os.getenv("GMAIL_TOKEN_JSON"))

    token_data = _json_from_env("GMAIL_TOKEN_JSON")
    if token_data:
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    elif os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if not token_from_env:
                with open("token.json", "w", encoding="utf-8") as token:
                    token.write(creds.to_json())
        else:
            credentials_data = _json_from_env("GMAIL_CREDENTIALS_JSON")

            if credentials_data:
                flow = InstalledAppFlow.from_client_config(
                    credentials_data, SCOPES
                )
            elif os.path.exists("credentials.json"):
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
            else:
                raise RuntimeError(
                    "Gmail credentials are missing. Configure GMAIL_TOKEN_JSON."
                )

            if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
                raise RuntimeError(
                    "Gmail token is missing/expired on Vercel. "
                    "Create/refresh token.json locally and set its JSON content "
                    "as GMAIL_TOKEN_JSON."
                )

            creds = flow.run_local_server(port=0)
            with open("token.json", "w", encoding="utf-8") as token:
                token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _decode(data):
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode(
        "utf-8", errors="ignore"
    )


def get_email_body(payload):
    body = ""
    parts = payload.get("parts", [])

    if parts:
        for part in parts:
            if part.get("parts"):
                body += get_email_body(part)
            elif part.get("mimeType") in ("text/plain", "text/html"):
                data = part.get("body", {}).get("data")
                if data:
                    body += _decode(data) + "\n"
    else:
        data = payload.get("body", {}).get("data")
        if data:
            body = _decode(data)

    return body


def get_job_emails(hours=24, max_results=100):
    """
    Fetch job-alert emails from the latest one-day window.
    For 24 hours Gmail uses newer_than:1d.
    """
    if hours <= 24:
        time_query = "newer_than:1d"
    else:
        days = max(1, (hours + 23) // 24)
        time_query = f"newer_than:{days}d"

    service = get_gmail_service()
    query = (
        f"{time_query} "
        "(from:(linkedin.com) OR from:(indeed.com) OR from:(naukri.com))"
    )

    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )

    emails = []
    for item in results.get("messages", []):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="full")
            .execute()
        )

        headers = msg.get("payload", {}).get("headers", [])
        header_map = {h["name"].lower(): h["value"] for h in headers}

        received_at = ""
        if msg.get("internalDate"):
            received_at = datetime.fromtimestamp(
                int(msg["internalDate"]) / 1000, tz=timezone.utc
            ).isoformat()

        emails.append(
            {
                "id": item["id"],
                "subject": header_map.get("subject", ""),
                "sender": header_map.get("from", ""),
                "body": get_email_body(msg.get("payload", {})),
                "received_at": received_at,
            }
        )

    emails.sort(key=lambda item: item.get("received_at", ""), reverse=True)
    return emails
