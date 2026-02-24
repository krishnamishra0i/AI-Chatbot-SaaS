@echo off
echo 🚀 Starting AI Avatar Chatbot - Backend and Frontend
echo =====================================================

echo 📦 Checking dependencies...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

echo 🔧 Setting up Python environment...
cd /d "%~dp0"

REM Add user site-packages to Python path
set PYTHONPATH=%APPDATA%\Python\Python314\site-packages;%PYTHONPATH%

echo 🖥️  Starting Backend Server (Port 8000)...
start "AI Avatar Backend" cmd /k "cd /d %~dp0 && python run_backend.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 🌐 Starting Frontend Server (Port 3000)...
start "AI Avatar Frontend" cmd /k "cd /d %~dp0src\frontend && npm run dev"

echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo 🎉 Both servers are starting up!
echo.
echo 🌐 Frontend: http://localhost:3001
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 💡 You can now:
echo    • Open the web interface at http://localhost:3000
echo    • Use the API directly at http://localhost:8000/api/chat
echo    • Test with: python interactive_chat.py
echo.
echo Press any key to close this window...
pause >nul