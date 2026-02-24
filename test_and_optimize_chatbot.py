#!/usr/bin/env python3
"""
PROJECT RUN AND OPTIMIZATION TEST
Run the chatbot and test/optimize answers
"""

import requests
import json
import time

def test_and_optimize_chatbot():
    """Test the chatbot and optimize answers"""
    
    print("="*80)
    print("🚀 RUNNING AND OPTIMIZING YOUR CHATBOT")
    print("="*80)
    
    # Test questions
    test_questions = [
        "what is lms",
        "how do i access my courses",
        "how do i cancel my subscription",
        "what are the best credit cards",
        "how should i budget my money",
        "what is compound interest",
        "what is artificial intelligence",
        "explain machine learning"
    ]
    
    print("\n🧪 TESTING CHATBOT RESPONSES...")
    print("-" * 60)
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/{len(test_questions)}")
        print(f"Q: {question}")
        
        try:
            # Test the chat endpoint
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8001/api/chat",
                json={
                    "message": question,
                    "language": "en",
                    "use_knowledge_base": True
                },
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '')
                sources = result.get('sources', [])
                
                print(f"✅ Status: {response.status_code}")
                print(f"⚡ Response Time: {response_time:.2f}s")
                print(f"📝 Answer: {answer[:200]}...")
                print(f"📊 Sources: {len(sources) if sources else 0}")
                
                # Quality assessment
                if len(answer) < 50:
                    assessment = "❌ POOR - Too short"
                elif "experiencing high demand" in answer.lower():
                    assessment = "❌ POOR - Generic response"
                elif "i don't know" in answer.lower():
                    assessment = "❌ POOR - No answer"
                elif len(answer) > 100 and "step" in answer.lower():
                    assessment = "✅ GOOD - Detailed answer"
                elif len(answer) > 150:
                    assessment = "✅ EXCELLENT - Comprehensive answer"
                else:
                    assessment = "👍 ACCEPTABLE - Decent answer"
                
                print(f"🏆 Assessment: {assessment}")
                
                results.append({
                    'question': question,
                    'status': response.status_code,
                    'response_time': response_time,
                    'answer_length': len(answer),
                    'answer': answer,
                    'assessment': assessment,
                    'sources_count': len(sources) if sources else 0
                })
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}...")
                
                results.append({
                    'question': question,
                    'status': response.status_code,
                    'response_time': response_time,
                    'answer_length': 0,
                    'answer': '',
                    'assessment': '❌ ERROR - Failed request',
                    'sources_count': 0
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'question': question,
                'status': 0,
                'response_time': 0,
                'answer_length': 0,
                'answer': '',
                'assessment': f'❌ ERROR - {str(e)}',
                'sources_count': 0
            })
        
        print("-" * 40)
    
    # Summary
    print("\n" + "="*80)
    print("📊 CHATBOT OPTIMIZATION RESULTS")
    print("="*80)
    
    if results:
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['status'] == 200)
        excellent_count = sum(1 for r in results if 'EXCELLENT' in r['assessment'])
        good_count = sum(1 for r in results if 'GOOD' in r['assessment'])
        acceptable_count = sum(1 for r in results if 'ACCEPTABLE' in r['assessment'])
        poor_count = sum(1 for r in results if 'POOR' in r['assessment'])
        error_count = sum(1 for r in results if 'ERROR' in r['assessment'])
        
        avg_response_time = sum(r['response_time'] for r in results if r['response_time'] > 0) / max(1, successful_tests)
        avg_answer_length = sum(r['answer_length'] for r in results) / total_tests
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"🌟️ Excellent: {excellent_count}/{total_tests} ({excellent_count/total_tests*100:.1f}%)")
        print(f"✅ Good: {good_count}/{total_tests} ({good_count/total_tests*100:.1f}%)")
        print(f"👍 Acceptable: {acceptable_count}/{total_tests} ({acceptable_count/total_tests*100:.1f}%)")
        print(f"❌ Poor: {poor_count}/{total_tests} ({poor_count/total_tests*100:.1f}%)")
        print(f"❌ Errors: {error_count}/{total_tests} ({error_count/total_tests*100:.1f}%)")
        print(f"⚡ Avg Response Time: {avg_response_time:.2f}s")
        print(f"📝 Avg Answer Length: {avg_answer_length:.0f} characters")
        
        # Optimization recommendations
        print("\n" + "="*80)
        print("🔧 OPTIMIZATION RECOMMENDATIONS")
        print("="*80)
        
        if error_count > 0:
            print(f"🚨 CRITICAL: {error_count} requests failed")
            print("   • Check if server is running on port 8001")
            print("   • Verify API endpoints are accessible")
            print("   • Check for import errors or missing dependencies")
        
        if poor_count > 0:
            print(f"⚠️ HIGH PRIORITY: {poor_count} poor responses")
            print("   • Generic responses detected - need better knowledge base")
            print("   • Short answers - need more detailed responses")
            print("   • Apply ultimate fix for maximum quality")
        
        if good_count + excellent_count >= total_tests * 0.8:
            print("✅ GOOD: Most responses are acceptable")
            print("   • Continue monitoring for consistency")
            print("   • Consider adding more detailed answers")
        
        if excellent_count >= total_tests * 0.9:
            print("🌟️ EXCELLENT: Chatbot is performing well!")
            print("   • Maintain current quality standards")
            print("   • Consider advanced optimizations")
        
        # Specific issues found
        print("\n🔍 SPECIFIC ISSUES FOUND:")
        for result in results:
            if 'ERROR' in result['assessment']:
                print(f"   ❌ {result['question']}: {result['assessment']}")
            elif 'POOR' in result['assessment']:
                print(f"   ⚠️ {result['question']}: {result['assessment']}")
        
        # Optimization actions
        print("\n🚀 OPTIMIZATION ACTIONS:")
        if poor_count > 0 or error_count > 0:
            print("   1. ✅ Apply ultimate fix from ultimate_chatbot_fix.py")
            print("   2. ✅ Update chat_routes.py with optimized version")
            print("   3. ✅ Restart server to apply changes")
            print("   4. ✅ Test again to verify improvements")
        else:
            print("   1. ✅ Monitor performance regularly")
            print("   2. ✅ Add more questions to knowledge base")
            print("   3. ✅ Consider AI API integration for unknown questions")
        
        # Success status
        print("\n" + "="*80)
        print("🎯 OPTIMIZATION STATUS")
        print("="*80)
        
        if error_count == 0 and poor_count == 0:
            print("🌟️ EXCELLENT: Chatbot is optimized and working perfectly!")
            print("   • All responses are good or excellent")
            print("   • No errors detected")
            print("   • Ready for production use")
        elif error_count == 0 and poor_count <= 2:
            print("✅ GOOD: Chatbot is working well with minor issues")
            print("   • Most responses are acceptable")
            print("   • Apply optimizations for best results")
        else:
            print("⚠️ NEEDS OPTIMIZATION: Chatbot requires improvements")
            print("   • Apply the ultimate fix immediately")
            print("   • Follow the optimization actions above")
    
    return results

if __name__ == '__main__':
    test_and_optimize_chatbot()
