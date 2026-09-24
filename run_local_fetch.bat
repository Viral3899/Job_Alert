@echo off
echo ==============================
echo Local Job Fetch - Run Once
echo ==============================

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the local fetch
python local_fetch.py

echo.
echo Done.
pause