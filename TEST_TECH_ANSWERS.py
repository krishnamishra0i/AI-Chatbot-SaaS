#!/usr/bin/env python3
"""
Test the updated accurate answer system with tech questions
"""
from simple_accurate_system import simple_accurate_system

print("\n" + "="*80)
print("TESTING UPDATED ACCURATE ANSWER SYSTEM")
print("="*80)

test_questions = [
    'what is ai',
    'what is deep learning',
    'what is aws',
    'what are ai assistants',
    'what is creditor academy',
    'what is azure',
    'what is machine learning',
    'what is natural language processing',
]

for q in test_questions:
    r = simple_accurate_system.get_answer(q)
    print(f"\nQ: {q}")
    print(f"A: {r['answer'][:130]}...")
    print(f"Confidence: {r['confidence']} | Method: {r['method']}")
    print("-" * 80)

print("\n✓ Test completed!\n")
