import base64
import json
import os
import time

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# modify is required because the monitor labels processed emails.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
PROCESSED_LABEL = "JOB_MONITOR_PROCESSED"


def _credentials_from_env():
    raw = os.getenv("GMAIL_TOKEN_JSON")
    if not raw:
        return None
    try:
        info = json.loads(raw)
        # Do not request a new scope during construction. We validate the
        # stored scopes below and force a fresh OAuth flow when gmail.modify
        # is not present.
        return Credentials.from_authorized_user_info(info)
    except Exception:
        return None


def _has_required_scope(creds):
    required = "https://www.googleapis.com/auth/gmail.modify"
    scopes = set(creds.scopes or [])
    return required in scopes


def _local_oauth_flow():
    if not os.path.exists("credentials.json"):
        raise RuntimeError("credentials.json is missing. Download your Google OAuth client credentials first.")
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    return flow.run_local_server(port=0)


def get_gmail_service():
    # A token created with gmail.readonly cannot be silently upgraded to
    # gmail.modify. It must be re-authorized. This was the source of the
    # invalid_scope/insufficientPermissions errors after the processed-label
    # feature was added.
    creds = _credentials_from_env()

    if creds is None and os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json")
        except Exception:
            creds = None

    needs_reauth = creds is None or not _has_required_scope(creds)

    if creds and creds.expired and creds.refresh_token and not needs_reauth:
        try:
            creds.refresh(Request())
        except Exception as exc:
            # Google returns invalid_scope when the refresh token does not
            # support the requested scope. Fall back to interactive OAuth.
            if "invalid_scope" in str(exc).lower() or "insufficient" in str(exc).lower():
                needs_reauth = True
                creds = None
            else:
                raise

    if needs_reauth or not creds or not creds.valid:
        if os.getenv("VERCEL"):
            raise RuntimeError(
                "GMAIL_TOKEN_JSON is missing, expired, or does not contain gmail.modify. "
                "Re-authorize locally with this version and then update GMAIL_TOKEN_JSON in Vercel."
            )

        # Remove the old local token so OAuth cannot keep reusing the
        # gmail.readonly token.
        try:
            if os.path.exists("token.json"):
                os.remove("token.json")
        except OSError:
            pass

        print("Gmail OAuth scope is outdated. Starting a fresh gmail.modify authorization...")
        creds = _local_oauth_flow()

    if not os.getenv("VERCEL"):
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _ensure_label(service):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label.get("name") == PROCESSED_LABEL:
            return label["id"]
    created = service.users().labels().create(
        userId="me",
        body={"name": PROCESSED_LABEL, "labelListVisibility": "labelShow", "messageListVisibility": "show"},
    ).execute()
    return created["id"]


def get_job_emails(lookback_hours=48):
    service = get_gmail_service()
    # Gmail broad query; exact filtering is performed below.
    query = 'newer_than:3d (from:(linkedin.com) OR from:(indeed.com) OR from:(naukri.com) OR from:(wellfound.com) OR from:(cutshort.io) OR from:(instahyre.com) OR from:(hirist.tech) OR from:(foundit.in) OR from:(timesjobs.com) OR from:(shine.com) OR from:(freshersworld.com))'
    result = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
    messages = result.get("messages", [])
    cutoff_ms = (time.time() - lookback_hours * 3600) * 1000
    emails = []

    for item in messages:
        msg = service.users().messages().get(userId="me", id=item["id"], format="full").execute()
        labels = msg.get("labelIds", [])
        internal_date = int(msg.get("internalDate", "0"))
        if internal_date < cutoff_ms:
            continue
        # Skip emails already processed by this monitor.
        label_id = None
        try:
            label_id = _ensure_label(service)
        except Exception:
            pass
        if label_id and label_id in labels:
            continue

        headers = {h["name"].lower(): h.get("value", "") for h in msg.get("payload", {}).get("headers", [])}
        emails.append({
            "id": item["id"],
            "subject": headers.get("subject", ""),
            "sender": headers.get("from", ""),
            "date": headers.get("date", ""),
            "body": extract_body(msg.get("payload", {})),
            "raw_html": extract_html(msg.get("payload", {})),
            "internal_date": internal_date,
        })

    print(f"Found {len(emails)} unprocessed job-alert email(s) within the last {lookback_hours} hours.")
    return emails


def extract_body(payload):
    data = payload.get("body", {}).get("data")
    if data:
        return _decode(data)
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return _decode(part["body"]["data"])
        if part.get("parts"):
            value = extract_body(part)
            if value:
                return value
    return ""


def extract_html(payload):
    data = payload.get("body", {}).get("data")
    if data and payload.get("mimeType") == "text/html":
        return _decode(data)
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
            return _decode(part["body"]["data"])
        if part.get("parts"):
            value = extract_html(part)
            if value:
                return value
    return ""


def _decode(data):
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="ignore")


def mark_emails_processed(message_ids):
    if not message_ids:
        return
    service = get_gmail_service()
    label_id = _ensure_label(service)
    for i in range(0, len(message_ids), 100):
        service.users().messages().batchModify(
            userId="me",
            body={"ids": message_ids[i:i+100], "addLabelIds": [label_id]},
        ).execute()
