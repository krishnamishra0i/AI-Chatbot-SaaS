"""
Whisper-based Speech-to-Text (ASR) module
"""
import numpy as np
from typing import Optional
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class WhisperASR:
    """Speech-to-Text using OpenAI Whisper"""
    
    def __init__(self, model_name="base", device="cpu"):
        """
        Initialize Whisper ASR
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: 'cpu' or 'cuda'
        """
        try:
            import whisper
            self.whisper = whisper
            self.device = device
            logger.info(f"Loading Whisper model: {model_name}")
            self.model = whisper.load_model(model_name, device=device)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error("Whisper is not installed. Install it with: pip install openai-whisper")
            raise
    
    def transcribe(self, audio_data, language: Optional[str] = None) -> dict:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data (numpy array, float32, 16kHz)
            language: Language code (e.g., 'en', 'es'). If None, auto-detect
            
        Returns:
            dict: Transcription result with 'text' and 'language' keys
        """
        try:
            result = self.model.transcribe(
                audio_data,
                language=language,
                verbose=False
            )
            
            return {
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "confidence": 0.9  # Whisper doesn't provide confidence
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "text": "",
                "language": "unknown",
                "error": str(e)
            }
    
    def transcribe_file(self, filepath: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio file
        
        Args:
            filepath: Path to audio file
            language: Language code
            
        Returns:
            dict: Transcription result
        """
        try:
            logger.info(f"Transcribing file: {filepath}")
            result = self.model.transcribe(filepath, language=language, verbose=False)
            return {
                "text": result["text"],
                "language": result.get("language", "unknown")
            }
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return {"text": "", "error": str(e)}
