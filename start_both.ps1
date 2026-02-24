#!/usr/bin/env pwsh

Write-Host "🚀 Starting AI Avatar Chatbot - Backend and Frontend" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>$null
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔧 Setting up Python environment..." -ForegroundColor Yellow
Set-Location $PSScriptRoot

# Add user site-packages to Python path
$pythonPath = "$env:APPDATA\Python\Python314\site-packages"
$env:PYTHONPATH = "$pythonPath;$env:PYTHONPATH"

Write-Host "🖥️  Starting Backend Server (Port 8000)..." -ForegroundColor Blue
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    python run_backend.py
}

Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🌐 Starting Frontend Server (Port 3000)..." -ForegroundColor Blue
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PSScriptRoot\src\frontend"
    npm run dev
}

Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "🎉 Both servers are running!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 You can now:" -ForegroundColor Yellow
Write-Host "   • Open the web interface at http://localhost:3000" -ForegroundColor White
Write-Host "   • Use the API directly at http://localhost:8000/api/chat" -ForegroundColor White
Write-Host "   • Test with: python interactive_chat.py" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Magenta

# Wait for user interrupt
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "🛑 Stopping servers..." -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
}