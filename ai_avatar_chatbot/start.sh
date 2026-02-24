#!/bin/bash
# Quick Start Script for AI Avatar Chatbot

echo "======================================"
echo "AI Avatar Chatbot - Quick Start"
echo "======================================"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

echo "✓ Python found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
python setup.py

# Print instructions
echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the LLM server (in a new terminal):"
echo "   ollama serve"
echo ""
echo "   Then in another terminal:"
echo "   ollama pull mistral"
echo ""
echo "2. Start the FastAPI backend:"
echo "   python -m backend.main"
echo ""
echo "3. Open the frontend in your browser:"
echo "   http://localhost:8000/static/index.html"
echo ""
echo "======================================"
