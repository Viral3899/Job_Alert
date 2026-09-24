@echo off
echo ==============================
echo Job Monitor Setup
echo ==============================

python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

python -m venv venv
call venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"

if not exist .env (
    copy .env.example .env
)

if not exist data mkdir data
if not exist logs mkdir logs

echo.
echo Setup complete.
echo.
echo Next:
echo 1. Put Gmail OAuth credentials in credentials.json
echo 2. Edit .env with Telegram credentials
echo 3. Run: venv\Scripts\python.exe main.py
echo.
echo Dev commands:
echo - ruff check .        # lint
echo - black .             # format
echo - mypy .              # type check
echo - pytest              # run tests
echo.
pause
