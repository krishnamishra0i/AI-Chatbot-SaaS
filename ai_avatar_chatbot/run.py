#!/usr/bin/env python
"""
Run the AI Avatar Chatbot backend
Usage: python -m backend.main
or: python run.py
"""

if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path
    
    # Ensure we're in the right directory
    app_dir = Path(__file__).parent
    sys.path.insert(0, str(app_dir))
    
    # Import after path setup
    from backend.config import API_HOST, API_PORT, DEBUG
    
    print(f"Starting AI Avatar Chatbot on {API_HOST}:{API_PORT}")
    print(f"Debug mode: {DEBUG}")
    print(f"Frontend: http://{API_HOST if API_HOST != '0.0.0.0' else 'localhost'}:{API_PORT}/static/index.html")
    print(f"API Docs: http://{API_HOST if API_HOST != '0.0.0.0' else 'localhost'}:{API_PORT}/docs")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        "backend.main_enhanced:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
