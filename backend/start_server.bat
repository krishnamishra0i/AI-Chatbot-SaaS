@echo off
REM Start Athena FastAPI backend (stable mode, no auto-reload)
cd /d "%~dp0"
echo Starting Athena FastAPI Backend on configured port...
set UVICORN_RELOAD=false
python run.py
pause
