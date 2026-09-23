# Job Monitor v2 — 48h AI/ML/GenAI Alerts

This version reads official job-alert emails in Gmail, looks back exactly 48 hours, scores jobs against an AI/ML/GenAI profile, sends jobs scoring 60%+ to Telegram, and uses a Gmail label for persistent deduplication.

## Important architecture

- Local Windows: `python main.py` checks every 20 minutes.
- Vercel: `/api/cron` runs once per cron invocation; `vercel.json` schedules it every 20 minutes.
- Vercel cannot keep an infinite Python process running. Cron invokes the function periodically.
- Vercel Hobby currently does not provide 20-minute cron frequency; current Vercel documentation describes Hobby cron as once per day, while Pro/Enterprise support per-minute schedules. Use Pro for `*/20` automation.
- Gmail OAuth must use `gmail.modify` in this version because the monitor adds `JOB_MONITOR_PROCESSED` to processed alert emails. This is how deduplication survives serverless restarts without a separate database.

## Local setup

1. Re-authorize Gmail after the scope change to `gmail.modify`.
2. Keep `credentials.json` in the project root.
3. Run:

```bash
python main.py
```

The first run creates `token.json`.

## Vercel setup

After local Gmail authorization, put the complete contents of `token.json` into the Vercel environment variable `GMAIL_TOKEN_JSON`.

Also add:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `JOB_LOOKBACK_HOURS=48`
- `MIN_MATCH_SCORE=60`
- `CRON_SECRET`

Deploy the project to Vercel and make sure the cron is attached to the Production deployment.

## Naukri URL handling

The parser now:

1. Reads HTML `<a href>` links instead of regex-only URLs.
2. Unwraps common redirect parameters.
3. Removes tracking parameters.
4. Accepts canonical `naukri.com/job-listings-...` links.
5. If an email only contains a generic/broken Naukri link, it sends a working Naukri search URL instead of a broken tracking URL.

## Match scoring

100-point rule-based score:

- Role: 40
- Location: 20
- Skills: up to 35
- Experience: up to 10
- Negative terms: penalty

Telegram only receives jobs at or above `MIN_MATCH_SCORE=60`.

## Recommended alert sources

Start with official email alerts from LinkedIn, Indeed, Naukri, Wellfound, Cutshort, Instahyre, Hirist, Foundit, TimesJobs, Shine, Freshersworld, and selected company career pages.

Avoid login automation/scraping where a site's terms or access controls prohibit it. Email alerts and official APIs/feeds are preferred.

## Tailored Resume Automation

For every job scoring at or above `MIN_MATCH_SCORE` (default 60), the monitor sends:
1. The job alert and apply link to Telegram.
2. A JD-specific ATS-tailored DOCX resume as a Telegram document.

The tailoring model is instructed to use only facts present in `resume_template.docx`; it must not invent experience or skills.

Required environment variables:
- `GROQ_API_KEY`
- `GROQ_MODEL` (default `openai/gpt-oss-120b`)
- `JOB_LOOKBACK_HOURS=48`
- `MIN_MATCH_SCORE=60`

For Vercel, also configure:
- `GMAIL_TOKEN_JSON` (the authorized Gmail token JSON, including refresh token)
- `CRON_SECRET`
- Telegram variables
- Groq variables

The Vercel endpoint is `/api/cron` and is scheduled every 20 minutes by `vercel.json`. Vercel plan limits can affect how frequently a cron can run.
