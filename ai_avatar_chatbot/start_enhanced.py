#!/usr/bin/env python
"""
Enhanced AI Avatar Chatbot - Complete Setup and Startup Script
This script handles all setup, dependency checks, and server startup
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print a nice banner"""
    print("\n" + "="*60)
    print("🤖 ENHANCED AI AVATAR CHATBOT - COMPLETE SETUP")
    print("="*60)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependencies():
    """Check and install required dependencies"""
    print("\n📦 Checking dependencies...")

    required_packages = [
        'fastapi', 'uvicorn', 'python-dotenv', 'requests',
        'openai-whisper', 'pyttsx3', 'torch', 'numpy'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n⚠️ Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False

    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")

    # Load .env file
    try:
        import dotenv
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            dotenv.load_dotenv(env_path)
            print("✅ .env file loaded")
        else:
            print("❌ .env file not found")
            return False
    except ImportError:
        print("❌ python-dotenv not available")
        return False

    # Check API key
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key and groq_key != 'your_groq_api_key_here':
        print("✅ Groq API key configured")
    else:
        print("⚠️ Groq API key not configured (will use fallback)")

    # Check LLM provider
    llm_provider = os.getenv('LLM_PROVIDER', 'groq')
    print(f"🤖 LLM Provider: {llm_provider}")

    return True

def test_groq_connection():
    """Test Groq API connection"""
    print("\n🔗 Testing Groq API connection...")

    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key or groq_key == 'your_groq_api_key_here':
        print("⚠️ Skipping Groq test (no API key)")
        return True

    try:
        import requests
        headers = {
            'Authorization': f'Bearer {groq_key}',
            'Content-Type': 'application/json'
        }

        # Simple test request
        response = requests.get('https://api.groq.com/openai/v1/models', headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ Groq API connection successful")
            return True
        else:
            print(f"❌ Groq API error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AI Avatar Chatbot server...")

    try:
        # Kill any existing processes
        print("🧹 Cleaning up old processes...")
        try:
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'],
                         capture_output=True, check=False)
            subprocess.run(['taskkill', '/f', '/im', 'uvicorn.exe'],
                         capture_output=True, check=False)
        except:
            pass

        time.sleep(2)

        # Start the server
        print("🎯 Starting server on http://localhost:8000")
        print("📱 Frontend will be available at http://localhost:3002")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)

        # Use subprocess to run the server
        cmd = [sys.executable, '-m', 'uvicorn', 'backend.main_enhanced:app',
               '--host', '0.0.0.0', '--port', '8000', '--reload']

        subprocess.run(cmd, cwd=Path(__file__).parent)

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        return False

    return True

def main():
    """Main setup and startup function"""
    print_banner()

    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Groq API", test_groq_connection),
    ]

    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False

    if not all_passed:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return False

    print("\n🎉 All checks passed! Starting server...")
    start_server()

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup and startup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)