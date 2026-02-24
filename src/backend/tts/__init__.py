"""TTS module"""
from .modern_tts import ModernTTS, XTTSVTS  # ModernTTS is preferred (supports Python 3.14+)
from .xtts_trainer import XTTSVoiceTrainer
from .audio_utils import AudioUtils

__all__ = ["ModernTTS", "XTTSVTS", "XTTSVoiceTrainer", "AudioUtils"]
