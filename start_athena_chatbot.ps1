#!/usr/bin/env powershell
# Athena LMS AI Chatbot - Quick Start (PowerShell)
# This script starts both the backend and opens the chatbot in a browser

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Athena LMS AI Chatbot Quick Start" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} Catch {
    Write-Host "✗ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.8+ from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    Exit 1
}

# Check if Flask is installed
Try {
    python -c "import flask" 2>&1 | Out-Null
    Write-Host "✓ Flask is installed" -ForegroundColor Green
} Catch {
    Write-Host "! Installing required packages..." -ForegroundColor Yellow
    pip install flask flask-cors
}

# Get the directory of this script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Cyan
Write-Host ""

# Start Python backend in a new PowerShell window
$backendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$scriptDir'; python athena_chatbot_backend.py`"" -PassThru

# Wait for server to start
Write-Host "Waiting for server to start (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if server is running
Try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -ErrorAction Stop
    Write-Host ""
    Write-Host "✓ Backend server is running successfully!" -ForegroundColor Green
    Write-Host ""
} Catch {
    Write-Host ""
    Write-Host "⚠ Warning: Backend server may not be running correctly" -ForegroundColor Yellow
    Write-Host "  Please check the terminal window for errors" -ForegroundColor Yellow
    Write-Host ""
}

# Open chatbot in default browser
Write-Host "Opening chatbot in your default browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

$htmlFile = Join-Path $scriptDir "athena_chatbot_ui_advanced.html"
Start-Process $htmlFile

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Athena AI Chatbot is Ready!" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Backend: http://localhost:5000" -ForegroundColor Green
Write-Host "✓ Frontend: Opening in your browser" -ForegroundColor Green
Write-Host ""
Write-Host "Features:" -ForegroundColor Cyan
Write-Host "  • Chat with AI" 
Write-Host "  • Voice input (click microphone)"
Write-Host "  • Voice output (AI speaks responses)"
Write-Host "  • Full conversation history"
Write-Host ""
Write-Host "To stop the backend, close the terminal window" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to continue"
