@echo off
setlocal

REM This is an optional local fallback scheduler.
REM For 24/7 operation while the PC is OFF, use an external scheduler
REM (for example cron-job.org) to call the Vercel URL every 15 minutes.

if "%CRON_SECRET%"=="" (
  echo ERROR: Set CRON_SECRET before running this script.
  exit /b 1
)

curl -sS -X GET "https://jobalert-nine.vercel.app/api/cron" ^
  -H "Authorization: Bearer %CRON_SECRET%"

echo.
echo API called at %date% %time%
endlocal
