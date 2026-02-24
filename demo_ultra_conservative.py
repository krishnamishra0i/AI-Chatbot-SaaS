#!/usr/bin/env python3
"""
ULTRA CONSERVATIVE TOKEN ADJUSTMENT SYSTEM DEMONSTRATION
Shows extremely short token limits for concise responses
"""

def analyze_question_context(question: str) -> dict:
    """
    Analyze question to determine emotional context and response requirements
    ULTRA CONSERVATIVE VERSION - Extremely short responses
    """
    question_lower = question.lower().strip()

    # Emotion and context detection
    emotional_indicators = {
        'greetings': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy', 'hiya'],
        'excited': ['wow', 'amazing', 'awesome', 'fantastic', 'incredible', 'brilliant', 'excellent'],
        'frustrated': ['why', 'what the hell', 'this sucks', 'terrible', 'awful', 'horrible', 'stupid'],
        'urgent': ['urgent', 'emergency', 'asap', 'immediately', 'right now', 'quickly'],
        'confused': ['confused', 'lost', 'don\'t understand', 'help me', 'stuck', 'not sure'],
        'grateful': ['thank you', 'thanks', 'appreciate', 'grateful', 'helpful']
    }

    # Question complexity indicators
    complexity_indicators = {
        'simple': ['what is', 'define', 'explain simply', 'basic', 'introduction to'],
        'detailed': ['how does', 'explain in detail', 'comprehensive', 'step by step', 'thorough'],
        'technical': ['algorithm', 'implementation', 'code', 'programming', 'technical'],
        'comparative': ['vs', 'versus', 'compare', 'difference between', 'better than']
    }

    # Length-based analysis
    question_length = len(question.split())

    # Detect emotion
    detected_emotions = []
    for emotion, keywords in emotional_indicators.items():
        if any(keyword in question_lower for keyword in keywords):
            detected_emotions.append(emotion)

    # Detect complexity
    detected_complexity = []
    for complexity, keywords in complexity_indicators.items():
        if any(keyword in question_lower for keyword in keywords):
            detected_complexity.append(complexity)

    # Determine response parameters based on analysis - ULTRA CONSERVATIVE
    base_tokens = 50  # Ultra conservative minimum tokens
    temperature = 0.3  # Conservative default

    # Adjust for emotions - extremely short responses
    if 'greetings' in detected_emotions:
        base_tokens = 20   # Ultra short, friendly responses
        temperature = 0.8  # More creative for friendly chat
    elif 'excited' in detected_emotions:
        base_tokens = 80
        temperature = 0.7  # Enthusiastic but controlled
    elif 'frustrated' in detected_emotions:
        base_tokens = 120
        temperature = 0.4  # More factual, less creative
    elif 'urgent' in detected_emotions:
        base_tokens = 40
        temperature = 0.2  # Quick, direct answers
    elif 'confused' in detected_emotions:
        base_tokens = 140
        temperature = 0.5  # Clear, explanatory
    elif 'grateful' in detected_emotions:
        base_tokens = 30
        temperature = 0.6  # Warm, appreciative

    # Adjust for complexity - extremely reduced
    if 'simple' in detected_complexity:
        base_tokens = min(base_tokens, 60)
        temperature = min(temperature, 0.4)
    elif 'detailed' in detected_complexity:
        base_tokens = max(base_tokens, 160)
        temperature = 0.3  # More precise for detailed explanations
    elif 'technical' in detected_complexity:
        base_tokens = max(base_tokens, 140)
        temperature = 0.2  # Very precise for technical content
    elif 'comparative' in detected_complexity:
        base_tokens = max(base_tokens, 130)
        temperature = 0.4  # Balanced for comparisons

    # Adjust for question length - very conservative
    if question_length < 5:  # Very short questions
        base_tokens = min(base_tokens, 35)
    elif question_length > 20:  # Long, complex questions
        base_tokens = max(base_tokens, 120)

    # Context-based adjustments for specific domains - extremely short
    if any(word in question_lower for word in ['lms', 'learning', 'course', 'education']):
        base_tokens = max(base_tokens, 100)  # Educational content - very concise
        temperature = 0.3  # More factual for educational content
    elif any(word in question_lower for word in ['code', 'programming', 'algorithm', 'debug']):
        base_tokens = max(base_tokens, 120)  # Code explanations - focused and brief
        temperature = 0.2  # Very precise for code
    elif any(word in question_lower for word in ['financial', 'money', 'budget', 'credit']):
        base_tokens = max(base_tokens, 110)  # Financial advice - concise
        temperature = 0.3  # Balanced but conservative

    # Ensure reasonable bounds - extremely conservative maximum
    max_tokens = max(15, min(base_tokens, 200))  # Between 15-200 tokens (ultra short!)
    temperature = max(0.1, min(temperature, 0.9))  # Between 0.1-0.9

    return {
        'max_tokens': max_tokens,
        'temperature': temperature,
        'detected_emotions': detected_emotions,
        'detected_complexity': detected_complexity,
        'question_length': question_length,
        'context_type': 'educational' if 'lms' in question_lower else
                       'technical' if any(word in question_lower for word in ['code', 'programming']) else
                       'financial' if any(word in question_lower for word in ['financial', 'money']) else
                       'general'
    }

def main():
    """Demonstrate the ultra conservative token adjustment system"""

    print("="*80)
    print("🚀 ULTRA CONSERVATIVE TOKEN ADJUSTMENT SYSTEM DEMONSTRATION")
    print("="*80)

    # Test questions with different emotions and contexts
    test_questions = [
        # Greetings - ultra short
        "Hi there!",
        "Hello, how are you?",
        "Good morning!",

        # Excited questions - short
        "Wow, this is amazing!",
        "That's fantastic! How does it work?",

        # Frustrated questions - medium short
        "Why is this not working?",
        "This sucks, what the hell is going on?",

        # Urgent questions - very short
        "Help me urgently!",
        "I need this ASAP!",

        # Confused questions - medium
        "I'm confused, can you explain this step by step?",
        "I'm lost, don't understand this at all",

        # Technical questions - focused
        "How does machine learning work?",
        "Explain the algorithm implementation",

        # Simple questions - very short
        "What is Python?",
        "Define artificial intelligence",

        # Educational/LMS questions - concise
        "How do I access my courses in LMS?",
        "What is Athena LMS?",

        # Financial questions - concise
        "How should I budget my money?",
        "What are the best credit cards?",

        # Long complex questions - still reasonable
        "Can you explain in detail how compound interest works and provide examples of how it affects long-term financial planning and investment strategies?"
    ]

    print("\n📊 ANALYZING QUESTION CONTEXT AND TOKEN ADJUSTMENT (ULTRA CONSERVATIVE)")
    print("-" * 80)

    for i, question in enumerate(test_questions, 1):
        print(f"\n{i:2d}. Question: '{question}'")

        # Analyze the question
        analysis = analyze_question_context(question)

        print(f"    📏 Length: {analysis['question_length']} words")
        print(f"    🎭 Emotions: {analysis['detected_emotions'] if analysis['detected_emotions'] else 'None'}")
        print(f"    🔧 Complexity: {analysis['detected_complexity'] if analysis['detected_complexity'] else 'None'}")
        print(f"    📂 Context: {analysis['context_type']}")
        print(f"    🔢 Max Tokens: {analysis['max_tokens']}")
        print(f"    🌡️  Temperature: {analysis['temperature']:.1f}")

        # Categorize response style
        if analysis['max_tokens'] <= 40:
            style = "Ultra Brief & Concise"
        elif analysis['max_tokens'] <= 80:
            style = "Very Short & Direct"
        elif analysis['max_tokens'] <= 140:
            style = "Short & Focused"
        else:
            style = "Medium & Essential"

        print(f"    🎨 Style: {style}")

    print("\n" + "="*80)
    print("✅ ULTRA CONSERVATIVE TOKEN ADJUSTMENT ANALYSIS COMPLETE")
    print("="*80)

    # Summary statistics
    analyses = [analyze_question_context(q) for q in test_questions]

    token_ranges = {
        'Ultra Brief (≤40)': sum(1 for a in analyses if a['max_tokens'] <= 40),
        'Very Short (41-80)': sum(1 for a in analyses if 41 <= a['max_tokens'] <= 80),
        'Short (81-140)': sum(1 for a in analyses if 81 <= a['max_tokens'] <= 140),
        'Medium (141-200)': sum(1 for a in analyses if 141 <= a['max_tokens'] <= 200)
    }

    print("\n📈 TOKEN DISTRIBUTION SUMMARY (ULTRA CONSERVATIVE):")
    for range_name, count in token_ranges.items():
        if count > 0:
            print(f"  {range_name}: {count} questions")

    avg_tokens = sum(a['max_tokens'] for a in analyses) / len(analyses)
    avg_temp = sum(a['temperature'] for a in analyses) / len(analyses)

    print(".1f")
    print(".2f")
    print("\n🚀 EXTREMELY SHORT RESPONSES - Maximum 200 tokens, average ~80 tokens!")
    print("💡 Answers will now be ultra-concise and to the point!")

if __name__ == "__main__":
    main()