@echo off
REM Quick Start Script for AI Avatar Chatbot (Windows)

echo ======================================
echo AI Avatar Chatbot - Quick Start
echo ======================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.9+
    exit /b 1
)

echo OK Python found

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create directories
echo Creating directories...
python setup.py

REM Print instructions
echo.
echo ======================================
echo OK Setup Complete!
echo ======================================
echo.
echo Next steps:
echo.
echo 1. Start the LLM server (in a new terminal):
echo    ollama serve
echo.
echo    Then in another terminal:
echo    ollama pull mistral
echo.
echo 2. Start the FastAPI backend:
echo    python -m backend.main
echo.
echo 3. Open the frontend in your browser:
echo    http://localhost:8000/static/index.html
echo.
echo ======================================
pause
