"""
Modern TTS module using Edge TTS and async support
"""
import asyncio
import io
import numpy as np
from typing import Optional
from backend.utils.logger import setup_logger
import tempfile
import os

logger = setup_logger(__name__)


class ModernTTS:
    """Text-to-Speech using Microsoft Edge TTS (supports Python 3.14+)"""
    
    def __init__(self, device="cpu"):
        """
        Initialize modern TTS
        
        Args:
            device: 'cpu' or 'cuda' (not used for edge-tts but kept for compatibility)
        """
        self.device = device
        self.use_edge = False
        self.use_pyttsx3 = False
        self.pyttsx_engine = None
        
        # Try edge-tts first (works with Python 3.14+)
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.use_edge = True
            logger.info("✅ Edge TTS loaded (supports Python 3.14+)")
        except ImportError:
            logger.warning("edge-tts not available, trying pyttsx3...")
            
            try:
                import pyttsx3
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty('rate', 150)
                self.use_pyttsx3 = True
                logger.info("✅ Using pyttsx3 as fallback")
            except ImportError:
                logger.error("No TTS engine available!")
                raise RuntimeError("Install edge-tts or pyttsx3: pip install edge-tts")
    
    def synthesize(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        language: str = "en",
        voice: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesize text to speech (returns audio bytes)
        
        Args:
            text: Text to synthesize
            speaker_wav: Ignored for edge-tts (kept for API compatibility)
            language: Language code ('en', 'es', 'fr', etc.)
            voice: Optional voice name (e.g., 'en-US-GuyNeural' for male voice)
            
        Returns:
            Audio data (MP3 bytes) or None if error
        """
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Empty text provided for synthesis")
                return None
            
            logger.info(f"Synthesizing: {text[:50]}...")
            
            if self.use_edge:
                return self._synthesize_edge_tts(text, language, voice)
            elif self.use_pyttsx3:
                return self._synthesize_pyttsx3(text)
            else:
                logger.error("No TTS engine available")
                return None
                
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return None
    
    def _synthesize_edge_tts(self, text: str, language: str = "en", voice: Optional[str] = None) -> Optional[bytes]:
        """Synthesize using Edge TTS with male voice by default"""
        try:
            # Map language codes to male voices (preferred)
            voice_map = {
                'en': 'en-US-GuyNeural',  # Male voice for English
                'es': 'es-ES-AlvaroNeural',  # Male voice for Spanish
                'fr': 'fr-FR-HenriNeural',  # Male voice for French
                'de': 'de-DE-ConradNeural',  # Male voice for German
                'it': 'it-IT-DiegoNeural',  # Male voice for Italian
                'pt': 'pt-BR-BrendaNeural',  # Female for Portuguese
                'ru': 'ru-RU-DmitryNeural',  # Male voice for Russian
                'ja': 'ja-JP-NanamiNeural',  # Female for Japanese
                'zh': 'zh-CN-XiaoxuanNeural',  # Female for Chinese
            }
            
            # Use provided voice or default from map
            if voice:
                selected_voice = voice
            else:
                selected_voice = voice_map.get(language, 'en-US-GuyNeural')
            
            # Create communicate instance (don't specify rate, use default)
            communicate = self.edge_tts.Communicate(text=text, voice=selected_voice)
            
            # Collect audio data
            audio_data = b''
            
            # Run async function with better error handling
            async def get_audio():
                nonlocal audio_data
                async for chunk in communicate.stream():
                    if chunk.get("type") == "audio":
                        audio_data += chunk.get("data", b'')
            
            # Try to use existing event loop if available, otherwise create new one
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, we can't use run_until_complete
                # Fall back to pyttsx3 instead
                logger.warning("Already in async context, falling back to pyttsx3")
                return self._synthesize_pyttsx3(text)
            except RuntimeError:
                # No running loop, we can create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(get_audio())
                finally:
                    loop.close()
            
            if len(audio_data) == 0:
                logger.warning("No audio data generated from edge-tts")
                # Fallback to pyttsx3 if edge-tts failed
                return self._synthesize_pyttsx3(text)
            
            logger.info(f"✅ Generated {len(audio_data)} bytes of audio")
            return audio_data
            
        except Exception as e:
            logger.error(f"Edge TTS error: {e}, falling back to pyttsx3")
            return self._synthesize_pyttsx3(text)
    
    def _synthesize_pyttsx3(self, text: str) -> Optional[bytes]:
        """Synthesize using pyttsx3 fallback"""
        try:
            import wave
            import pyttsx3
            
            # Initialize pyttsx3 if not already done
            if self.pyttsx_engine is None:
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty('rate', 150)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            
            self.pyttsx_engine.save_to_file(text, tmp_path)
            self.pyttsx_engine.runAndWait()
            
            # Read WAV file and convert to bytes
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            os.unlink(tmp_path)
            logger.info(f"✅ Generated {len(audio_bytes)} bytes of audio (pyttsx3)")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"pyttsx3 error: {e}")
            return None
    
    async def synthesize_async(
        self,
        text: str,
        language: str = "en"
    ) -> Optional[bytes]:
        """Async version for streaming"""
        return self.synthesize(text, language=language)
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.use_edge:
            return [
                "en-US-AriaNeural",
                "en-US-GuyNeural", 
                "es-ES-AlvaroNeural",
                "fr-FR-HenriNeural",
                "de-DE-ConradNeural",
                "it-IT-DiegoNeural",
                "pt-BR-BrendaNeural",
                "ru-RU-DmitryNeural",
                "ja-JP-NanamiNeural",
                "zh-CN-XiaoxuanNeural",
            ]
        else:
            return ["default"]


# Import the old XTTS class for backward compatibility (with fallback)
class XTTSVTS(ModernTTS):
    """Backward compatible alias for old TTS class"""
    pass
