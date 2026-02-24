@echo off
REM Athena LMS AI Chatbot - Quick Start
REM This script starts both the backend and opens the chatbot in a browser

echo.
echo ====================================
echo Athena LMS AI Chatbot Quick Start
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask flask-cors
)

REM Get the directory of this script
set "script_dir=%~dp0"

echo.
echo Starting backend server...
echo.

REM Start Python backend in a new window
start "Athena Chatbot Backend" cmd /k "cd /d "%script_dir%" && python athena_chatbot_backend.py"

REM Wait for server to start
echo Waiting for server to start (5 seconds)...
timeout /t 5 /nobreak

REM Check if server is running
echo Checking if server is running...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" >nul 2>&1

if errorlevel 1 (
    echo.
    echo Warning: Backend server may not be running correctly
    echo Please check the terminal window for errors
    echo.
) else (
    echo.
    echo ✓ Backend server is running successfully!
    echo.
)

REM Open chatbot in default browser
echo Opening chatbot in your default browser...
timeout /t 2 /nobreak

REM Get the absolute path to the HTML file
set "html_file=%script_dir%athena_chatbot_ui_advanced.html"

REM Convert to file:// URL format
for /f "tokens=*" %%A in ('powershell -Command "Write-Host 'file:///%cd:\=//%/athena_chatbot_ui_advanced.html'"') do set "html_url=%%A"

REM Open in browser
start "" "%html_file%"

echo.
echo ====================================
echo Athena AI Chatbot is Ready!
echo ====================================
echo.
echo ✓ Backend: http://localhost:5000
echo ✓ Frontend: Opening in your browser
echo.
echo Features:
echo - Chat with AI
echo - Voice input (click microphone)
echo - Voice output (AI speaks responses)
echo - Full conversation history
echo.
echo To stop the backend, close the terminal window
echo.
pause
