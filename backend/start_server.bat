@echo off
REM Start Athena backend with TTS/STT support (no auto-reload)
cd /d "%~dp0"
echo Starting Athena Flask Backend (TTS/STT enabled)...
echo Disabling auto-reload to prevent import issues...
python -m flask run --no-reload
pause
