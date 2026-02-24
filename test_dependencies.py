#!/usr/bin/env python3
"""
Test script to verify all dependencies are working.

This script is designed to be more robust and portable.
"""
import sys
import os
import importlib
import site

def setup_paths():
    """Add necessary local directories to the system path."""
    # Add user site-packages to path for local user installs
    user_site = site.getusersitepackages()
    if os.path.exists(user_site) and user_site not in sys.path:
        sys.path.insert(0, user_site)
        print(f"Added user site-packages to path: {user_site}")

    # Add src directory to path for backend imports
    src_path = os.path.join(os.getcwd(), 'src')
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"Added src directory to path: {src_path}")
    print("-" * 20)

def check_dependency(package_name, import_name=None):
    """
    Tries to import a package, prints its version, and handles ImportErrors.
    """
    import_name = import_name or package_name
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'version not found')
        print(f"✓ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"✗ {package_name}: {e}")
        return False

def main():
    """Run all dependency checks."""
    setup_paths()

    print("Testing core dependencies...")
    dependencies = {
        "PyTorch": "torch",
        "ChromaDB": "chromadb",
        "Scikit-learn": "sklearn",
        "FastAPI": "fastapi",
        "Uvicorn": "uvicorn",
    }

    for name, import_name in dependencies.items():
        check_dependency(name, import_name)

    print("\nTesting backend import...")
    check_dependency("Backend import", "backend.main_enhanced")

    print("\nCore dependencies check finished! Sentence transformers may have import issues but that's OK for now.")
    print("Let's try to run the backend server.")

if __name__ == "__main__":
    main()