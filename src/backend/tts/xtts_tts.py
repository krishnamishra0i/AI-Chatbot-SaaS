"""
XTTS (Cross-Lingual Text-to-Speech) module
"""
import numpy as np
from typing import Optional
from backend.utils.logger import setup_logger
import os
import tempfile

logger = setup_logger(__name__)

class XTTSVTS:
    """Text-to-Speech using XTTS v2 with fallback to pyttsx3"""
    
    def __init__(self, device="cpu"):
        """
        Initialize TTS - tries XTTS first, falls back to pyttsx3
        
        Args:
            device: 'cpu' or 'cuda'
        """
        self.device = device
        self.use_fallback = False
        self.model = None
        self.tts_lib = None
        
        # Try XTTS first (requires Python 3.6-3.12)
        try:
            from TTS.api import TTS  # type: ignore
            self.tts_lib = TTS
            logger.info("Loading XTTS v2 model...")
            self.model = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                device=device,
                gpu_verbose=False
            )
            logger.info("✅ XTTS v2 model loaded successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"XTTS not available: {e}")
            logger.info("Falling back to pyttsx3 for TTS...")
            
            try:
                import pyttsx3
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty('rate', 150)
                self.use_fallback = True
                logger.info("✅ Using pyttsx3 as fallback (works with Python 3.14)")
            except ImportError:
                logger.error("Neither TTS nor pyttsx3 installed!")
                logger.error("Install with: pip install TTS pyttsx3")
                raise RuntimeError("No TTS engine available")
    
    
    def synthesize(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        language: str = "en"
    ) -> Optional[np.ndarray]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            speaker_wav: Path to reference speaker WAV file (for voice cloning, XTTS only)
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Audio data (numpy array, 24kHz for XTTS or 44.1kHz for pyttsx3) or None if error
        """
        try:
            logger.info(f"Synthesizing: {text[:50]}...")
            
            if self.use_fallback:
                # Use pyttsx3 fallback
                import io
                import wave
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name
                
                self.pyttsx_engine.save_to_file(text, tmp_path)
                self.pyttsx_engine.runAndWait()
                
                # Read WAV file
                with wave.open(tmp_path, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                
                os.unlink(tmp_path)
                logger.info(f"✅ Generated audio: {len(audio)} samples")
                return audio
            else:
                # Use XTTS
                if not self.model:
                    logger.error("TTS model not initialized")
                    return None
                
                if speaker_wav:
                    audio = self.model.tts(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language
                    )
                else:
                    audio = self.model.tts(
                        text=text,
                        language=language
                    )
                
                return np.array(audio, dtype=np.float32)
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return None
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speaker_wav: Optional[str] = None,
        language: str = "en"
    ) -> bool:
        """
        Synthesize speech and save to file
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            speaker_wav: Reference speaker WAV file (XTTS only)
            language: Language code
            
        Returns:
            True if successful
        """
        try:
            if self.use_fallback:
                # Use pyttsx3 fallback
                self.pyttsx_engine.save_to_file(text, output_path)
                self.pyttsx_engine.runAndWait()
                logger.info(f"✅ TTS output saved to {output_path}")
                return True
            else:
                # Use XTTS
                if not self.model:
                    logger.error("TTS model not initialized")
                    return False
                
                self.model.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path
                )
                logger.info(f"✅ TTS output saved to {output_path}")
                return True
        except Exception as e:
            logger.error(f"TTS file save error: {e}")
            return False
