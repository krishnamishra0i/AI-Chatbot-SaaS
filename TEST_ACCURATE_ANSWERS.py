#!/usr/bin/env python3
"""
Test the Simple Accurate Answer System
"""
from simple_accurate_system import simple_accurate_system

print("\n" + "="*70)
print("TESTING CREDITOR ACADEMY ACCURATE ANSWER SYSTEM")
print("="*70)

# Test key questions
questions = [
    'hello',
    'hi',
    'what is creditor academy',
    'creditor academy',
    'what is the freedom formula',
    'freedom formula',
    'what is sovereignty',
    'sovereignty',
    'what courses do you offer',
    'what is a business trust',
    'how do i access my courses',
    'what is lms'
]

for q in questions:
    result = simple_accurate_system.get_answer(q)
    print(f"\nQuestion: {q}")
    print(f"Confidence: {result['confidence']} ({result['accuracy_level']})")
    print(f"Method: {result['method']}")
    print(f"Answer: {result['answer'][:120]}...")
    print("-" * 70)

print("\n✓ All tests completed!\n")
