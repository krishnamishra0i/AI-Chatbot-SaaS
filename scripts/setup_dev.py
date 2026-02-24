#!/usr/bin/env python3
"""
AI Avatar Chatbot - Development Environment Setup Script
This script sets up the complete development environment for the AI Avatar Chatbot project.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.10+")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def setup_virtual_environment():
    """Create and activate virtual environment."""
    if os.path.exists(".venv"):
        print("⚠️  Virtual environment already exists")
        return True

    # Create virtual environment
    if not run_command("python -m venv .venv", "Creating virtual environment"):
        return False

    # Upgrade pip
    pip_path = ".venv/Scripts/pip" if platform.system() == "Windows" else ".venv/bin/pip"
    if not run_command(f"{pip_path} install --upgrade pip", "Upgrading pip"):
        return False

    print("✅ Virtual environment created successfully")
    return True

def install_dependencies():
    """Install Python dependencies."""
    pip_path = ".venv/Scripts/pip" if platform.system() == "Windows" else ".venv/bin/pip"

    # Install core dependencies
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing Python dependencies"):
        return False

    print("✅ Dependencies installed successfully")
    return True

def setup_frontend():
    """Setup frontend development environment."""
    frontend_dir = Path("src/frontend")
    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found")
        return True

    os.chdir(frontend_dir)

    # Check if node_modules exists
    if os.path.exists("node_modules"):
        print("⚠️  Frontend dependencies already installed")
    else:
        # Install Node.js dependencies
        if not run_command("npm install", "Installing frontend dependencies"):
            os.chdir("../..")
            return False

    os.chdir("../..")
    print("✅ Frontend setup completed")
    return True

def create_env_file():
    """Create .env file from template."""
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        return True

    template_file = ".env.example"
    if not os.path.exists(template_file):
        print("⚠️  .env.example template not found")
        # Create a basic .env file
        env_content = """# AI Avatar Chatbot Environment Configuration

# Server Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=true

# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
CHROMA_DB_PATH=./data/merged_chroma_db

# Audio Configuration
TTS_ENGINE=edge_tts
STT_ENGINE=whisper

# Logging
LOG_LEVEL=INFO

# Security (change these in production!)
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Optional: External Services
REDIS_URL=redis://localhost:6379
PROMETHEUS_PORT=9090
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Basic .env file created")
        print("⚠️  Please update the API keys and configuration values")
    else:
        shutil.copy(template_file, ".env")
        print("✅ .env file created from template")

    return True

def setup_git_hooks():
    """Setup pre-commit git hooks."""
    if not os.path.exists(".git"):
        print("⚠️  Not a git repository, skipping git hooks setup")
        return True

    # Check if pre-commit is available
    pip_path = ".venv/Scripts/pip" if platform.system() == "Windows" else ".venv/bin/pip"
    result = run_command(f"{pip_path} install pre-commit", "Installing pre-commit")
    if not result:
        return False

    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False

    print("✅ Git hooks setup completed")
    return True

def run_initial_tests():
    """Run basic tests to verify setup."""
    print("🧪 Running initial tests...")

    # Test Python imports
    python_cmd = ".venv/Scripts/python" if platform.system() == "Windows" else ".venv/bin/python"

    test_commands = [
        (f'{python_cmd} -c "import fastapi, uvicorn; print(\'FastAPI imports OK\')"', "Testing FastAPI import"),
        (f'{python_cmd} -c "import torch; print(f\'PyTorch {torch.__version__} OK\')"', "Testing PyTorch import"),
        (f'{python_cmd} -c "import chromadb; print(\'ChromaDB OK\')"', "Testing ChromaDB import"),
    ]

    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            return False

    print("✅ Initial tests passed")
    return True

def create_startup_scripts():
    """Create convenient startup scripts."""
    if platform.system() == "Windows":
        # Create batch file for Windows
        batch_content = """@echo off
echo Starting AI Avatar Chatbot...

REM Activate virtual environment
call .venv\\Scripts\\activate.bat

REM Start the backend server
python -m src.backend.main_enhanced

pause
"""
        with open("start.bat", "w") as f:
            f.write(batch_content)

        # Create PowerShell script
        ps1_content = """# AI Avatar Chatbot Startup Script

Write-Host "Starting AI Avatar Chatbot..." -ForegroundColor Green

# Activate virtual environment
& ".venv\\Scripts\\Activate.ps1"

# Start the backend server
python -m src.backend.main_enhanced
"""
        with open("start.ps1", "w") as f:
            f.write(ps1_content)

    else:
        # Create shell script for Unix-like systems
        shell_content = """#!/bin/bash
echo "Starting AI Avatar Chatbot..."

# Activate virtual environment
source .venv/bin/activate

# Start the backend server
python -m src.backend.main_enhanced
"""
        with open("start.sh", "w") as f:
            f.write(shell_content)
        os.chmod("start.sh", 0o755)

    print("✅ Startup scripts created")
    return True

def main():
    """Main setup function."""
    print("🚀 AI Avatar Chatbot - Development Environment Setup")
    print("=" * 60)

    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    steps = [
        ("Checking Python version", check_python_version),
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up frontend", setup_frontend),
        ("Creating environment file", create_env_file),
        ("Setting up git hooks", setup_git_hooks),
        ("Running initial tests", run_initial_tests),
        ("Creating startup scripts", create_startup_scripts),
    ]

    completed_steps = 0
    for step_name, step_func in steps:
        print(f"\n📋 Step {completed_steps + 1}: {step_name}")
        if step_func():
            completed_steps += 1
        else:
            print(f"\n❌ Setup failed at step: {step_name}")
            print("Please check the error messages above and try again.")
            sys.exit(1)

    print(f"\n🎉 Setup completed successfully! ({completed_steps}/{len(steps)} steps)")
    print("\n📝 Next steps:")
    print("1. Update your .env file with API keys")
    print("2. Run 'python -m src.backend.main_enhanced' to start the backend")
    print("3. Open another terminal and run 'npm run dev' in src/frontend/ for the frontend")
    print("4. Visit http://localhost:8000 to access the application")
    print("\n📚 Useful commands:")
    print("- Backend: python -m src.backend.main_enhanced")
    print("- Frontend: cd src/frontend && npm run dev")
    print("- Tests: python -m pytest tests/")
    print("- Format code: black src/ && isort src/")

if __name__ == "__main__":
    main()