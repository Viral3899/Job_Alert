@echo off
echo ==============================
echo Job Monitor API Scheduler (15 min)
echo ==============================

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the scheduler
python api_scheduler.py

echo.
echo Scheduler stopped.
pause