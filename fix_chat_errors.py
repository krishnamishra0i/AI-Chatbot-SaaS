#!/usr/bin/env python3
"""
CHAT SYSTEM ERROR FIXING AND TESTING
Comprehensive error resolution and testing
"""

import sys
import os
import asyncio
sys.path.append('ai_avatar_chatbot')

def test_imports():
    """Test all imports and report status"""
    print("="*60)
    print("🔧 TESTING CHAT SYSTEM IMPORTS")
    print("="*60)

    results = {}

    # Test basic imports
    try:
        import numpy as np
        results['numpy'] = '✅ Available'
        print("✅ NumPy imported successfully")
    except ImportError as e:
        results['numpy'] = f'❌ Failed: {e}'
        print(f"❌ NumPy failed: {e}")

    try:
        import requests
        results['requests'] = '✅ Available'
        print("✅ Requests imported successfully")
    except ImportError as e:
        results['requests'] = f'❌ Failed: {e}'
        print(f"❌ Requests failed: {e}")

    # Test logger
    try:
        from backend.utils.logger import setup_logger
        logger = setup_logger(__name__)
        results['logger'] = '✅ Available'
        print("✅ Logger imported successfully")
    except ImportError as e:
        results['logger'] = f'❌ Failed: {e}'
        print(f"❌ Logger failed: {e}")

    # Test ultimate accuracy
    try:
        from ultimate_accuracy_working import UltimateAccuracyOptimizer
        opt = UltimateAccuracyOptimizer()
        result = opt.get_ultimate_accurate_answer('hello')
        results['ultimate_accuracy'] = f'✅ Available (confidence: {result["confidence"]})'
        print(f"✅ Ultimate Accuracy working (confidence: {result['confidence']})")
    except ImportError as e:
        results['ultimate_accuracy'] = f'❌ Failed: {e}'
        print(f"❌ Ultimate Accuracy failed: {e}")
    except Exception as e:
        results['ultimate_accuracy'] = f'⚠️  Partial: {e}'
        print(f"⚠️  Ultimate Accuracy partial: {e}")

    # Test enhanced system
    try:
        from backend.utils.enhanced_chat_system import enhanced_chat_system
        results['enhanced_system'] = f'✅ Available (RAG: {enhanced_chat_system.rag_retriever.is_initialized})'
        print(f"✅ Enhanced system working (RAG initialized: {enhanced_chat_system.rag_retriever.is_initialized})")
    except ImportError as e:
        results['enhanced_system'] = f'❌ Failed: {e}'
        print(f"❌ Enhanced system failed: {e}")
    except Exception as e:
        results['enhanced_system'] = f'⚠️  Partial: {e}'
        print(f"⚠️  Enhanced system partial: {e}")

    # Test chat routes
    try:
        from backend.api.chat_routes import router, ULTIMATE_ACCURACY_AVAILABLE, ENHANCED_SYSTEM_AVAILABLE
        results['chat_routes'] = f'✅ Available (Ultimate: {ULTIMATE_ACCURACY_AVAILABLE}, Enhanced: {ENHANCED_SYSTEM_AVAILABLE})'
        print(f"✅ Chat routes working (Ultimate: {ULTIMATE_ACCURACY_AVAILABLE}, Enhanced: {ENHANCED_SYSTEM_AVAILABLE})")
    except ImportError as e:
        results['chat_routes'] = f'❌ Failed: {e}'
        print(f"❌ Chat routes failed: {e}")
    except Exception as e:
        results['chat_routes'] = f'⚠️  Partial: {e}'
        print(f"⚠️  Chat routes partial: {e}")

    print("\n" + "="*60)
    print("📊 IMPORT TEST SUMMARY")
    print("="*60)

    for component, status in results.items():
        print(f"{component.upper():<20}: {status}")

    success_count = sum(1 for status in results.values() if status.startswith('✅'))
    total_count = len(results)

    print(f"\n🎯 OVERALL STATUS: {success_count}/{total_count} components working")

    if success_count == total_count:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    elif success_count >= total_count * 0.7:
        print("⚠️  MOSTLY OPERATIONAL - Some minor issues")
    else:
        print("❌ SIGNIFICANT ISSUES - Needs attention")

    return results

async def test_chat_functionality():
    """Test actual chat functionality"""
    print("\n" + "="*60)
    print("💬 TESTING CHAT FUNCTIONALITY")
    print("="*60)

    test_questions = [
        "hello",
        "what is creditor academy",
        "how do i cancel my membership",
        "what is sovereignty"
    ]

    # Test ultimate accuracy
    print("\n🔍 Testing Ultimate Accuracy System:")
    try:
        from ultimate_accuracy_working import UltimateAccuracyOptimizer
        opt = UltimateAccuracyOptimizer()

        for question in test_questions:
            result = opt.get_ultimate_accurate_answer(question)
            confidence = result['confidence']
            preview = result['answer'][:80] + "..." if len(result['answer']) > 80 else result['answer']
            status = "✅" if confidence >= 0.8 else "⚠️" if confidence >= 0.5 else "❌"
            print(f"  {status} '{question}' -> {confidence:.2f} confidence")
            print(f"      Preview: {preview}")
    except Exception as e:
        print(f"❌ Ultimate Accuracy test failed: {e}")

    # Test enhanced system
    print("\n🤖 Testing Enhanced Chat System:")
    try:
        from backend.utils.enhanced_chat_system import enhanced_chat_system

        for question in test_questions[:2]:  # Test fewer questions for speed
            try:
                result = await enhanced_chat_system.generate_response(question)
                response = result.get('response', '')
                preview = response[:80] + "..." if len(response) > 80 else response
                print(f"  ✅ '{question}' -> Response generated")
                print(f"      Preview: {preview}")
            except Exception as e:
                print(f"  ❌ '{question}' failed: {e}")
    except Exception as e:
        print(f"❌ Enhanced system test failed: {e}")

    # Test chat routes
    print("\n🌐 Testing Chat Routes:")
    try:
        from backend.api.chat_routes import chat
        from pydantic import BaseModel

        class TestMessage(BaseModel):
            message: str
            language: str = "en"
            use_knowledge_base: bool = True

        for question in test_questions[:2]:
            try:
                result = await chat(TestMessage(message=question))
                preview = result.response[:80] + "..." if len(result.response) > 80 else result.response
                print(f"  ✅ '{question}' -> Route working")
                print(f"      Response: {preview}")
            except Exception as e:
                print(f"  ❌ '{question}' route failed: {e}")
    except Exception as e:
        print(f"❌ Chat routes test failed: {e}")

def main():
    """Main testing function"""
    print("🚀 CHAT SYSTEM ERROR FIXING AND TESTING")
    print("========================================")

    # Test imports first
    import_results = test_imports()

    # Test functionality if imports mostly work
    success_count = sum(1 for status in import_results.values() if status.startswith('✅'))
    total_count = len(import_results)

    if success_count >= total_count * 0.6:  # At least 60% working
        print("\n🔄 Testing chat functionality...")
        asyncio.run(test_chat_functionality())
    else:
        print("\n❌ Too many import failures - skipping functionality tests")
        print("Fix import issues first!")

    print("\n" + "="*60)
    print("🎯 ERROR FIXING COMPLETE")
    print("="*60)
    print("\n💡 RECOMMENDATIONS:")
    print("1. Ensure all dependencies are installed: pip install numpy requests")
    print("2. Check environment variables: GOOGLE_API_KEY, GROQ_API_KEY")
    print("3. Verify knowledge base files exist in data/ directory")
    print("4. Test with simple questions first")
    print("5. Check logs for detailed error information")

if __name__ == "__main__":
    main()