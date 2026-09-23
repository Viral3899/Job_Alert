import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def _decode(data):
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

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

def get_job_emails():
    service = get_gmail_service()
    query = "newer_than:2d (from:(linkedin.com) OR from:(indeed.com) OR from:(naukri.com))"

    results = service.users().messages().list(
        userId="me", q=query, maxResults=100
    ).execute()

    emails = []
    for item in results.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=item["id"], format="full"
        ).execute()
        headers = msg["payload"].get("headers", [])
        header_map = {h["name"].lower(): h["value"] for h in headers}

        emails.append({
            "id": item["id"],
            "subject": header_map.get("subject", ""),
            "sender": header_map.get("from", ""),
            "body": get_email_body(msg["payload"]),
        })
    return emails
