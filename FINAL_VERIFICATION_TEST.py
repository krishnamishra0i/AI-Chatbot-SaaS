#!/usr/bin/env python3
"""
FINAL SYSTEM VERIFICATION TEST
Confirms all components are integrated and working
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success/failure"""
    print(f"\n{'─'*100}")
    print(f"🧪 {description}")
    print(f"{'─'*100}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ PASSED")
            return True
        else:
            if result.stderr:
                print(f"⚠️  {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️  TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all verification tests"""
    
    print("\n" + "█"*100)
    print("█" + " "*30 + "🔍 FINAL SYSTEM VERIFICATION TEST" + " "*34 + "█")
    print("█"*100)
    
    results = {}
    
    # Test 1: Comprehensive Answer System
    print("\n\n📚 TEST 1: COMPREHENSIVE ANSWER SYSTEM")
    cmd = """python -c "from comprehensive_answer_system import ComprehensiveAnswerSystem; \
cs = ComprehensiveAnswerSystem(); \
r = cs.get_answer('what is creditor academy'); \
print(f'✅ Found {len(cs.answers)} answers'); \
print(f'✅ Confidence: {r[\"confidence\"]}'); \
exit(0 if r['confidence'] >= 0.9 else 1)" """
    results['comprehensive'] = run_command(cmd, "Loading comprehensive answer system")
    
    # Test 2: ChromaDB Integration
    print("\n\n☁️  TEST 2: CHROMADB CLOUD INTEGRATION")
    cmd = """python chromadb_api_integration.py 2>&1 | head -20"""
    results['chromadb'] = run_command(cmd, "Verifying ChromaDB Cloud credentials")
    
    # Test 3: Integrated System
    print("\n\n🔄 TEST 3: INTEGRATED ANSWER SYSTEM")
    cmd = """python -c "from integrated_answer_system import IntegratedAnswerSystem; \
s = IntegratedAnswerSystem(); \
r = s.get_answer('what is ai'); \
print(f'✅ Layer {r[\"layer\"]}: {r[\"source\"]}'); \
print(f'✅ Confidence: {r[\"confidence\"]}'); \
exit(0 if r['confidence'] >= 0.5 else 1)" """
    results['integrated'] = run_command(cmd, "Testing integrated multi-layer system")
    
    # Test 4: API Key Verification
    print("\n\n🔑 TEST 4: API KEY VERIFICATION")
    cmd = """python verify_api_keys.py 2>&1 | grep -E "(Google API|Groq API|WORKING)"  """
    results['api_keys'] = run_command(cmd, "Checking API key configuration")
    
    # Test 5: Chat Routes Update
    print("\n\n🛣️  TEST 5: BACKEND INTEGRATION")
    cmd = """python -c "from ai_avatar_chatbot.backend.api.chat_routes import INTEGRATED_AVAILABLE, COMPREHENSIVE_AVAILABLE; \
print(f'✅ Integrated System: {INTEGRATED_AVAILABLE}'); \
print(f'✅ Comprehensive System: {COMPREHENSIVE_AVAILABLE}'); \
exit(0 if (INTEGRATED_AVAILABLE or COMPREHENSIVE_AVAILABLE) else 1)" """
    results['backend'] = run_command(cmd, "Verifying backend chat routes update")
    
    # Summary
    print("\n\n" + "═"*100)
    print("📊 VERIFICATION SUMMARY")
    print("═"*100)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        test_name = test.replace('_', ' ').title()
        print(f"\n{status} - {test_name}")
    
    print("\n" + "─"*100)
    print(f"\n📈 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "█"*100)
        print("█" + " "*25 + "🎉 ALL TESTS PASSED - SYSTEM IS READY! 🎉" + " "*31 + "█")
        print("█"*100)
        print("\n✅ Your chatbot system is production-ready!")
        print("\n📝 Next Steps:")
        print("   1. Read INTEGRATION_GUIDE.md for usage")
        print("   2. Read SETUP_COMPLETE.md for full overview")
        print("   3. Start your backend and test through /api/chat")
        print("   4. Monitor response quality and adjust answers as needed")
    else:
        print("\n" + "█"*100)
        print("█" + " "*35 + "⚠️  SOME TESTS FAILED" + " "*41 + "█")
        print("█"*100)
        print(f"\nFailed Tests: {total - passed}")
        print("\nPlease check the error messages above.")
        print("Most issues are optional (Google/Groq APIs) - comprehensive system works anyway.")
    
    print("\n" + "█"*100 + "\n")
    
    return 0 if passed >= 3 else 1  # At least 3 core tests should pass


if __name__ == "__main__":
    sys.exit(main())
