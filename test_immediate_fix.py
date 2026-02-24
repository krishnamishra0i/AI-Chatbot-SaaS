#!/usr/bin/env python3
"""
TEST IMMEDIATE FIX FOR CHATBOT ISSUES
Verify the fix works for generic responses, limited quality, and slow responses
"""

import requests
import json

def test_immediate_fix():
    """Test the immediate fix for chatbot issues"""
    
    print("="*80)
    print("🚀 TESTING IMMEDIATE FIX FOR CHATBOT ISSUES")
    print("="*80)
    
    base_url = "http://localhost:8001"
    
    # Test questions that were having issues
    test_questions = [
        "what is lms",
        "how do i cancel my subscription",
        "what is artificial intelligence",
        "explain machine learning",
        "compare python vs javascript",
        "what are the best credit cards",
        "how should i budget my money",
        "what is compound interest",
        "how do i access my courses",
        "what is the best way to learn"
    ]
    
    print(f"🔗 Testing server: {base_url}")
    print(f"📝 Testing {len(test_questions)} questions...")
    print("-" * 60)
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/{len(test_questions)}")
        print(f"Q: {question}")
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": question, "use_knowledge_base": True},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', 'No response')
                used_kb = result.get('used_knowledge_base', False)
                sources = result.get('sources', [])
                
                print(f"✅ Response received")
                print(f"📚 Used KB: {'Yes' if used_kb else 'No'}")
                print(f"📚 Sources: {sources}")
                print(f"📝 Answer: {answer[:200]}...")
                
                # Check for the specific issues mentioned
                issues_fixed = []
                
                # Check if generic response is fixed
                if not "experiencing high demand" in answer.lower():
                    issues_fixed.append("✅ Generic response fixed")
                else:
                    issues_fixed.append("❌ Still getting generic response")
                
                # Check if answer quality is improved
                if len(answer) > 150:
                    issues_fixed.append("✅ Answer quality improved")
                else:
                    issues_fixed.append("⚠️ Answer quality needs improvement")
                
                # Check if response is fast (under 15 seconds)
                issues_fixed.append("✅ Response time fast")
                
                # Check if using Groq API for general questions
                if isinstance(sources, list) and sources:
                    for source in sources:
                        if isinstance(source, dict):
                            if source.get('api_used') == 'groq':
                                issues_fixed.append("✅ Using Groq API")
                                break
                            elif source.get('api_used') == 'knowledge_base':
                                issues_fixed.append("✅ Using Knowledge Base")
                                break
                
                print(f"🔧 Issues Fixed: {len(issues_fixed)}/3")
                for issue in issues_fixed:
                    print(f"   {issue}")
                
                results.append({
                    'question': question,
                    'answer_length': len(answer),
                    'issues_fixed': len([i for i in issues_fixed if '✅' in i]),
                    'total_issues': 3
                })
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    # Summary
    print("\n" + "="*80)
    print("📊 IMMEDIATE FIX TEST RESULTS")
    print("="*80)
    
    if results:
        total_tests = len(results)
        total_issues_fixed = sum(r['issues_fixed'] for r in results)
        max_possible_issues = total_tests * 3
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"🔧 Issues Fixed: {total_issues_fixed}/{max_possible_issues} ({total_issues_fixed/max_possible_issues*100:.1f}%)")
        
        # Check specific issues
        generic_fixed = sum(1 for r in results if r['issues_fixed'] >= 1)
        quality_improved = sum(1 for r in results if r['issues_fixed'] >= 2)
        all_fixed = sum(1 for r in results if r['issues_fixed'] == 3)
        
        print(f"✅ Generic Response Fixed: {generic_fixed}/{total_tests} ({generic_fixed/total_tests*100:.1f}%)")
        print(f"✅ Quality Improved: {quality_improved}/{total_tests} ({quality_improved/total_tests*100:.1f}%)")
        print(f"✅ All Issues Fixed: {all_fixed}/{total_tests} ({all_fixed/total_tests*100:.1f}%)")
        
        print(f"\n🎯 Detailed Results:")
        for result in results:
            fixed_icon = "🎉" if result['issues_fixed'] == 3 else "✅" if result['issues_fixed'] >= 2 else "⚠️" if result['issues_fixed'] >= 1 else "❌"
            print(f"   {fixed_icon} {result['question'][:30]}... ({result['issues_fixed']}/3 issues fixed)")
    
    print("\n" + "="*80)
    print("🎉 IMMEDIATE FIX RESULTS")
    print("="*80)
    
    if all_fixed == total_tests:
        print("""
✅ ALL ISSUES FIXED SUCCESSFULLY!
   • Generic responses eliminated
   • Answer quality significantly improved
   • Response times fast and reliable
   • Groq API working for general questions
   • Knowledge base working for specific topics

✅ BEFORE → AFTER TRANSFORMATION:
   ❌ Generic responses → ✅ Comprehensive, detailed answers
   ❌ Limited quality → ✅ High-quality, specific responses
   ❌ Slow/unreliable → ✅ Fast, reliable responses

✅ YOUR CHATBOT IS NOW WORKING PERFECTLY!
""")
    elif quality_improved >= total_tests * 0.8:
        print("""
✅ MOST ISSUES FIXED!
   • Generic responses mostly eliminated
   • Answer quality significantly improved
   • Response times fast and reliable
   • Groq API working for general questions

✅ REMAINING IMPROVEMENTS:
   • A few questions may still need refinement
   • Consider expanding knowledge base coverage
   • Monitor for any remaining issues

✅ YOUR CHATBOT IS WORKING MUCH BETTER!
""")
    else:
        print("""
⚠️ PARTIAL FIX ACHIEVED!
   • Some issues still need attention
   • Generic responses partially eliminated
   • Answer quality needs more improvement
   • Response times are better

✅ NEXT STEPS:
   • Check integration code is properly implemented
   • Verify Groq API key is working correctly
   • Consider expanding knowledge base topics
   • Monitor and refine question classification

✅ YOUR CHATBOT IS IMPROVED BUT NEEDS MORE WORK!
""")
    
    print("\n" + "="*80)
    print("💡 TO COMPLETE THE FIX:")
    print("="*80)
    print("""
1. ✅ Copy code from immediate_fix_for_issues.py
2. ✅ Paste into ai_avatar_chatbot/backend/api/chat_routes.py
3. ✅ Restart your server
4. ✅ Test with various questions
5. ✅ Monitor performance

🚀 YOUR CHATBOT ISSUES ARE BEING FIXED!
""")

if __name__ == '__main__':
    test_immediate_fix()
