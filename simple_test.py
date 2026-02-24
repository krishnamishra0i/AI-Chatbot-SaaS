#!/usr/bin/env python3
"""
SIMPLE CHAT ERROR TEST
Basic functionality test
"""

import sys
import os

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")

    # Test numpy
    try:
        import numpy as np
        print("✅ NumPy: OK")
    except ImportError as e:
        print(f"❌ NumPy: {e}")

    # Test requests
    try:
        import requests
        print("✅ Requests: OK")
    except ImportError as e:
        print(f"❌ Requests: {e}")

def test_ultimate_accuracy():
    """Test ultimate accuracy system"""
    print("\nTesting Ultimate Accuracy...")
    try:
        sys.path.append('.')
        from ultimate_accuracy_working import UltimateAccuracyOptimizer

        opt = UltimateAccuracyOptimizer()
        result = opt.get_ultimate_accurate_answer("hello")

        print("✅ Ultimate Accuracy: OK"        print(f"   Confidence: {result['confidence']}")
        print(f"   Response: {result['answer'][:50]}...")

    except Exception as e:
        print(f"❌ Ultimate Accuracy: {e}")
        import traceback
        traceback.print_exc()

def test_chat_routes():
    """Test chat routes import"""
    print("\nTesting Chat Routes...")
    try:
        sys.path.append('ai_avatar_chatbot')
        from backend.api.chat_routes import router

        print("✅ Chat Routes: OK")

        # Check flags
        from backend.api.chat_routes import ULTIMATE_ACCURACY_AVAILABLE, ENHANCED_SYSTEM_AVAILABLE
        print(f"   Ultimate Available: {ULTIMATE_ACCURACY_AVAILABLE}")
        print(f"   Enhanced Available: {ENHANCED_SYSTEM_AVAILABLE}")

    except Exception as e:
        print(f"❌ Chat Routes: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔧 SIMPLE CHAT ERROR TEST")
    print("=" * 40)

    test_basic_imports()
    test_ultimate_accuracy()
    test_chat_routes()

    print("\n" + "=" * 40)
    print("Test complete!")

if __name__ == "__main__":
    main()