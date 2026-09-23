# Job Monitor / Job Alert API

This project reads official job-alert emails from Gmail (LinkedIn, Indeed and Naukri), parses them, matches them against the AI/ML profile, and can send matching jobs to Telegram.

## What changed

- `main.py` now exports a FastAPI application as `app`, so Vercel can run it.
- `GET /jobs/latest` fetches job-alert emails from the latest 24 hours.
- `GET /api/jobs` is an alias for the same endpoint.
- `GET /health` is a health check.
- `GET /docs` exposes Swagger/OpenAPI documentation.
- Local background monitoring is still available with `python main.py`.
- Gmail credentials can be supplied through environment variables for Vercel.

## API

Examples:

```text
GET /jobs/latest
GET /jobs/latest?limit=50
GET /jobs/latest?limit=50&min_score=60
GET /api/jobs
GET /health
```

The latest-job endpoints use the Gmail query:

```text
newer_than:1d
```

and only search alerts from LinkedIn, Indeed and Naukri.

## Local setup

Use Python 3.10+:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`.

For local Gmail OAuth, place your OAuth client file at:

```text
credentials.json
```

On the first local run:

```powershell
python main.py
```

A browser opens for Gmail authorization and creates `token.json`.

To run only the API locally:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/docs
```

## Vercel deployment

Do **not** upload these files:

- `.env`
- `credentials.json`
- `token.json`
- `venv/`
- `data/jobs.db`

Instead add the Gmail OAuth values to Vercel Project Settings -> Environment Variables.

### `GMAIL_TOKEN_JSON`

Copy the complete JSON contents of your local `token.json` and store it as the `GMAIL_TOKEN_JSON` environment variable.

### `GMAIL_CREDENTIALS_JSON`

Only needed when the application needs the OAuth client configuration. Store the complete contents of your OAuth client JSON.

Also configure:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
MIN_MATCH_SCORE
CHECK_INTERVAL_MINUTES
```

Vercel serverless functions should be used for the API. The continuous `while True` monitor in `main.py` is for local/worker execution and should not be expected to run continuously inside a Vercel request.

## Security

Never commit API keys, Telegram bot tokens, Gmail OAuth credentials, `token.json`, or `.env`.
