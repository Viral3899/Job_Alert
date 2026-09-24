@echo off
echo ==============================
echo Job Monitor - API Server + Scheduler
echo ==============================

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Starting API Server on port 8001...
start "JobMonitor API" cmd /k "call venv\Scripts\activate.bat && python api_server.py"

echo Waiting for server to start...
timeout /t 3 >nul

echo Starting Scheduler (15 min intervals)...
start "JobMonitor Scheduler" cmd /k "call venv\Scripts\activate.bat && python api_scheduler.py"

echo.
echo Both started in separate windows.
echo - API Server: http://localhost:8001
echo - Health: http://localhost:8001/health
echo - Cron: http://localhost:8001/api/cron
echo.
echo Press Ctrl+C in each window to stop.
pause