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

if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv

echo Installing dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt

if not exist .env (
    copy .env.example .env
)

if not exist data mkdir data

echo.
echo ==============================
echo SETUP COMPLETE
echo ==============================
echo.
echo Next steps:
echo.
echo 1. Add Gmail credentials:
echo    credentials.json
echo.
echo 2. Edit:
echo    .env
echo.
echo 3. Run:
echo    venv\Scripts\python.exe main.py
echo.
pause