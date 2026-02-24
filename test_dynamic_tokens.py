what i want to make this front add on my background and make a pop chatbot #!/usr/bin/env python3
"""
TEST DYNAMIC TOKEN ADJUSTMENT SYSTEM
Demonstrates how the chatbot analyzes questions and adjusts token limits based on emotion and context
"""

import sys
sys.path.append('ai_avatar_chatbot')

from ultimate_chatbot_fix import UltimateChatbotFix
from ultimate_accuracy_working import UltimateAccuracyOptimizer
from simple_accurate_system import simple_accurate_system

def test_dynamic_token_adjustment():
    """Test the dynamic token adjustment system"""

    print("="*80)
    print("🧪 TESTING DYNAMIC TOKEN ADJUSTMENT SYSTEM")
    print("="*80)

    # Initialize the chatbot fix
    chatbot = UltimateChatbotFix()

    # Test questions with different emotions and contexts
    test_questions = [
        # Greetings - should be short and creative
        "Hi there!",
        "Hello, how are you?",
        "Good morning!",

        # Excited questions - medium length, enthusiastic
        "Wow, this is amazing!",
        "That's fantastic! How does it work?",

        # Frustrated questions - longer, more factual
        "Why is this not working?",
        "This sucks, what the hell is going on?",

        # Urgent questions - short, direct
        "Help me urgently!",
        "I need this ASAP!",

        # Confused questions - longer, explanatory
        "I'm confused, can you explain this step by step?",
        "I'm lost, don't understand this at all",

        # Technical questions - detailed, precise
        "How does machine learning work?",
        "Explain the algorithm implementation",

        # Simple questions - shorter, straightforward
        "What is Python?",
        "Define artificial intelligence",

        # Educational/LMS questions - detailed, factual
        "How do I access my courses in LMS?",
        "What is Athena LMS?",

        # Financial questions - detailed, conservative
        "How should I budget my money?",
        "What are the best credit cards?",

        # Long complex questions - longer responses
        "Can you explain in detail how compound interest works and provide examples of how it affects long-term financial planning and investment strategies?"
    ]

    print("\n📊 ANALYZING QUESTION CONTEXT AND TOKEN ADJUSTMENT (CONSERVATIVE VERSION)")
    print("-" * 80)

    for i, question in enumerate(test_questions, 1):
        print(f"\n{i:2d}. Question: '{question}'")

        # Analyze the question
        analysis = chatbot.analyze_question_context(question)

        print(f"    📏 Length: {analysis['question_length']} words")
        print(f"    🎭 Emotions: {analysis['detected_emotions'] if analysis['detected_emotions'] else 'None'}")
        print(f"    🔧 Complexity: {analysis['detected_complexity'] if analysis['detected_complexity'] else 'None'}")
        print(f"    📂 Context: {analysis['context_type']}")
        print(f"    🔢 Max Tokens: {analysis['max_tokens']}")
        print(f"    🌡️  Temperature: {analysis['temperature']:.1f}")

        # Categorize response style
        if analysis['max_tokens'] <= 100:
            style = "Very Short & Creative"
        elif analysis['max_tokens'] <= 200:
            style = "Short & Friendly"
        elif analysis['max_tokens'] <= 400:
            style = "Medium & Balanced"
        else:
            style = "Long & Detailed"

        print(f"    🎨 Style: {style}")

    print("\n" + "="*80)
    print("✅ DYNAMIC TOKEN ADJUSTMENT ANALYSIS COMPLETE")
    print("="*80)

    # Summary statistics
    analyses = [chatbot.analyze_question_context(q) for q in test_questions]

    token_ranges = {
        'Very Short (≤60)': sum(1 for a in analyses if a['max_tokens'] <= 60),
        'Short (61-120)': sum(1 for a in analyses if 61 <= a['max_tokens'] <= 120),
        'Medium (121-240)': sum(1 for a in analyses if 121 <= a['max_tokens'] <= 240),
        'Long (241-320)': sum(1 for a in analyses if 241 <= a['max_tokens'] <= 320),
        'Very Long (321+)': sum(1 for a in analyses if a['max_tokens'] > 320)
    }

    print("\n📈 TOKEN DISTRIBUTION SUMMARY (CONSERVATIVE):")
    for range_name, count in token_ranges.items():
        if count > 0:
            print(f"  {range_name}: {count} questions")

    avg_tokens = sum(a['max_tokens'] for a in analyses) / len(analyses)
    avg_temp = sum(a['temperature'] for a in analyses) / len(analyses)

    print(".1f")
    print(".2f")
    print("\n✅ Much more conservative token limits for shorter, focused responses!")

    # Test with the ultimate accuracy optimizer
    print("\n🧪 TESTING ULTIMATE ACCURACY OPTIMIZER")
    opt = UltimateAccuracyOptimizer()
    result = opt.get_ultimate_accurate_answer("What is the difference between a chatbot and an AI assistant?")
    print(f"Confidence: {result['confidence']} - {result['accuracy_level']}")

if __name__ == "__main__":
    test_dynamic_token_adjustment()

# Test the system
from simple_accurate_system import simple_accurate_system

result = simple_accurate_system.get_answer("what is creditor academy")
print(result['answer'])  # Accurate sovereignty education info
print(result['confidence'])  # 0.99 (99% confidence)