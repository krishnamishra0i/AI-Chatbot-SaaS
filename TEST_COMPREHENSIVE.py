#!/usr/bin/env python3
"""
Test the improved comprehensive answer system
"""
from comprehensive_answer_system import comprehensive_system

print("\n" + "="*100)
print("TESTING COMPREHENSIVE ANSWER SYSTEM - 200+ ACCURATE ANSWERS")
print("="*100)

test_questions = [
    # Creditor Academy
    ('what is creditor academy', 'Creditor Academy'),
    ('freedom formula', 'Freedom Formula'),
    ('what is sovereignty', 'Sovereignty'),
    ('business trust', 'business trust'),
    
    # Technology
    ('what is ai', 'Artificial Intelligence'),
    ('what is machine learning', 'Machine Learning'),
    ('what is aws', 'Amazon Web Services'),
    ('python programming', 'Python'),
    
    # Business & Finance
    ('what is business', 'Business'),
    ('what is marketing', 'marketing'),
    ('what is investment', 'Investment'),
    ('how do i save money', 'save money'),
    
    # General
    ('what is education', 'Education'),
    ('what is leadership', 'leadership'),
    ('what is innovation', 'Innovation'),
]

print(f"\nTesting {len(test_questions)} different questions:\n")

passed = 0
for question, expected_keyword in test_questions:
    result = comprehensive_system.get_answer(question)
    has_keyword = expected_keyword.lower() in result['answer'].lower()
    status = "✅" if has_keyword else "❌"
    passed += 1 if has_keyword else 0
    
    print(f"{status} Q: {question}")
    print(f"   Confidence: {result['confidence']} | Method: {result['method']}")
    print(f"   Answer: {result['answer'][:100]}...")
    print()

print("="*100)
print(f"RESULTS: {passed}/{len(test_questions)} tests passed ({int(100*passed/len(test_questions))}%)")
print("="*100 + "\n")
