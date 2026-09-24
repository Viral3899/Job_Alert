@echo off
echo ==============================
echo Job Monitor API Server (Port 8001)
echo ==============================

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the API server
python api_server.py

echo.
echo Server stopped.
pause