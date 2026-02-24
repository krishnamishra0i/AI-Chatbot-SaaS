
def truncate_response_by_tokens(text, max_tokens=200):
    """Truncate response by token count (approximate)"""
    words = text.split()
    tokens = len(words)  # Rough approximation
    if tokens <= max_tokens:
        return text
    return ' '.join(words[:max_tokens]) + '...'

def analyze_question_for_truncation(question):
    """Analyze question to determine response length"""
    # Longer questions may need shorter responses
    if len(question) < 20:
        return 100
    elif len(question) < 50:
        return 150
    else:
        return 200
