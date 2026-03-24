"""
Configuration for Token & Length Optimization
Controls response limits for chat, TTS, and STT.
"""

# ════════════════════════════════════════════════════════════════════
# CHAT RESPONSE LIMITS (Per Tier)
# ════════════════════════════════════════════════════════════════════

CHAT_LIMITS = {
    "demo": {
        "max_tokens": 100,           # Short responses for demo
        "max_chars": 500,            # ~2 sentences
        "max_message_length": 100,   # User input limit
    },
    "starter": {
        "max_tokens": 500,           # ~400 words
        "max_chars": 2000,           # Medium responses
        "max_message_length": 500,
    },
    "pro": {
        "max_tokens": 1000,          # ~800 words
        "max_chars": 4000,           # Longer responses
        "max_message_length": 2000,
    },
    "unlimited": {
        "max_tokens": 2000,          # Full responses
        "max_chars": 8000,           # No practical limit
        "max_message_length": 9999,
    },
}


# ════════════════════════════════════════════════════════════════════
# TTS OPTIMIZATION
# ════════════════════════════════════════════════════════════════════

TTS_SETTINGS = {
    "demo": {
        "max_chars": 500,             # ~10 seconds of speech
        "chunk_size": 100,            # Break into small chunks
        "optimize": True,             # Enable cost optimization
    },
    "starter": {
        "max_chars": 2000,            # ~40 seconds
        "chunk_size": 500,
        "optimize": True,
    },
    "pro": {
        "max_chars": 5000,            # ~2+ minutes
        "chunk_size": 1000,
        "optimize": False,            # High-quality TTS
    },
    "unlimited": {
        "max_chars": 10000,           # Full audio
        "chunk_size": 2000,
        "optimize": False,
    },
}


# ════════════════════════════════════════════════════════════════════
# STT OPTIMIZATION
# ════════════════════════════════════════════════════════════════════

STT_SETTINGS = {
    "demo": {
        "max_duration_seconds": 30,   # 30 seconds max
        "sample_rate": 16000,         # Standard quality
        "optimize": True,             # Faster transcription
    },
    "starter": {
        "max_duration_seconds": 120,  # 2 minutes max
        "sample_rate": 16000,
        "optimize": True,
    },
    "pro": {
        "max_duration_seconds": 600,  # 10 minutes max
        "sample_rate": 44100,         # Higher quality
        "optimize": False,
    },
    "unlimited": {
        "max_duration_seconds": 3600, # 1 hour max
        "sample_rate": 44100,
        "optimize": False,
    },
}


# ════════════════════════════════════════════════════════════════════
# TOKEN OPTIMIZATION
# ════════════════════════════════════════════════════════════════════

TOKEN_OPTIMIZATION = {
    "demo": {
        "enabled": True,
        "compression_level": "aggressive",  # Shorter prompts
        "system_prompt_type": "minimal",    # Short system prompt
        "cache_responses": True,            # Cache common Q&A
    },
    "starter": {
        "enabled": True,
        "compression_level": "moderate",
        "system_prompt_type": "standard",
        "cache_responses": True,
    },
    "pro": {
        "enabled": False,
        "compression_level": "none",
        "system_prompt_type": "detailed",
        "cache_responses": False,
    },
    "unlimited": {
        "enabled": False,
        "compression_level": "none",
        "system_prompt_type": "detailed",
        "cache_responses": False,
    },
}


# ════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════

def get_chat_limit(tier: str) -> dict:
    """Get chat limits for tier."""
    return CHAT_LIMITS.get(tier, CHAT_LIMITS["demo"])


def get_tts_limit(tier: str) -> dict:
    """Get TTS limits for tier."""
    return TTS_SETTINGS.get(tier, TTS_SETTINGS["demo"])


def get_stt_limit(tier: str) -> dict:
    """Get STT limits for tier."""
    return STT_SETTINGS.get(tier, STT_SETTINGS["demo"])


def should_optimize(tier: str, service: str) -> bool:
    """Check if optimization is enabled for service."""
    if service == "chat":
        return TOKEN_OPTIMIZATION[tier]["enabled"]
    elif service == "tts":
        return TTS_SETTINGS[tier]["optimize"]
    elif service == "stt":
        return STT_SETTINGS[tier]["optimize"]
    return False


# ════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES (Token-optimized)
# ════════════════════════════════════════════════════════════════════

SYSTEM_PROMPTS = {
    "minimal": "You are a helpful AI assistant. Keep responses under 100 words.",
    
    "standard": """You are Athena, a helpful AI assistant for the Athena AI Chat Platform.
    
    Guidelines:
    - Be concise and helpful
    - Answer questions directly
    - Keep responses focused
    - Use short paragraphs""",
    
    "detailed": """You are Athena, a sophisticated AI assistant powering the Athena AI Chat Platform.
    
    Your role:
    - Provide helpful, accurate, and detailed responses
    - Engage in meaningful conversations
    - Explain complex topics clearly
    - Ask clarifying questions when needed
    
    Guidelines:
    - Be professional but friendly
    - Support multiple languages
    - Provide relevant examples
    - Ask follow-up questions if helpful""",
}


def get_system_prompt(tier: str) -> str:
    """Get system prompt for tier (token-optimized)."""
    prompt_type = TOKEN_OPTIMIZATION[tier]["system_prompt_type"]
    return SYSTEM_PROMPTS.get(prompt_type, SYSTEM_PROMPTS["standard"])
