#!/bin/bash

echo "🚀 Starting AI Avatar Chatbot - Backend and Frontend"
echo "====================================================="

echo "📦 Checking dependencies..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

echo "✅ Python and Node.js found"

echo "🔧 Setting up Python environment..."
cd "$(dirname "$0")"

# Add user site-packages to Python path
export PYTHONPATH="$HOME/.local/lib/python3.*/site-packages:$PYTHONPATH"

echo "🖥️  Starting Backend Server (Port 8000)..."
python run_backend.py &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🌐 Starting Frontend Server (Port 3000)..."
cd src/frontend
npm run dev &
FRONTEND_PID=$!

echo "⏳ Waiting for frontend to start..."
sleep 10

echo "🎉 Both servers are running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 You can now:"
echo "   • Open the web interface at http://localhost:3000"
echo "   • Use the API directly at http://localhost:8000/api/chat"
echo "   • Test with: python interactive_chat.py"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait