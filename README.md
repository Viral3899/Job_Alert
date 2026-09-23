# Job Monitor

Monitors LinkedIn, Indeed, and Naukri job-alert emails in Gmail, filters them against an AI/ML profile, stores jobs in SQLite, and sends matching jobs to Telegram.

## Important
This project reads official job-alert emails. It does not log into or scrape LinkedIn, Indeed, or Naukri.

## Setup

### 1. Python
Use Python 3.10+.

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Gmail API
1. Open Google Cloud Console.
2. Create/select a project.
3. Enable the Gmail API.
4. Create OAuth Client ID -> Desktop app.
5. Download the JSON credentials.
6. Rename it to `credentials.json`.
7. Put it in this project folder.

On the first run, a browser will open for Gmail authorization. `token.json` is then created automatically.

### 3. Telegram
1. Open Telegram and message `@BotFather`.
2. Run `/newbot`.
3. Copy the bot token.
4. Message your new bot and send `/start`.
5. Put the bot token and chat ID in `.env`.

Create `.env` from `.env.example`.

### 4. Job alerts
Create official alerts on LinkedIn, Indeed, and Naukri for:
- AI/ML Engineer
- AI Engineer
- Generative AI Engineer
- GenAI Engineer
- Machine Learning Engineer
- LLM Engineer
- RAG Engineer
- Data Scientist

Locations:
- Remote
- Rajkot
- Ahmedabad
- Gandhinagar / GIFT City

The Gmail reader searches recent messages from LinkedIn/Indeed/Naukri.

### 5. Run

```powershell
python main.py
```

The first run authorizes Gmail. Then the monitor checks every 20 minutes.

## Windows startup
For 24/7 local monitoring, use Windows Task Scheduler to start:

`venv\Scripts\python.exe main.py`

at Windows login.

## Notes
- Match scoring is rule-based in this starter version.
- `data/jobs.db` is created automatically.
- Duplicate jobs are detected using a hash.
- Tune keywords and score thresholds in `config.py`.
