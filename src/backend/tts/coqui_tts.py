"""
Coqui TTS - Free and Open Source Text-to-Speech
Alternative to paid TTS services like Edge TTS or Google TTS
"""
import torch
import numpy as np
import io
import tempfile
from typing import Optional, Union, Any
from pathlib import Path
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

try:
    from TTS.api import TTS  # type: ignore
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    logger.warning("Coqui TTS not installed. Install with: pip install TTS")

class CoquiTTS:
    """
    Free and Open Source Text-to-Speech using Coqui TTS
    Completely local, no API keys or internet required
    """
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC", device: str = "cpu"):
        """
        Initialize Coqui TTS
        
        Args:
            model_name: TTS model name from Coqui model zoo
            device: Device for inference (cpu/cuda)
        """
        if not COQUI_AVAILABLE:
            raise ImportError("Coqui TTS not installed. Install with: pip install TTS")
        
        self.model_name = model_name
        self.device = device
        self.tts = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the TTS model"""
        try:
            logger.info(f"🎵 Initializing Coqui TTS: {self.model_name}")
            
            # Initialize TTS with the specified model
            self.tts = TTS(self.model_name, progress_bar=False)
            
            # Move to device if CUDA available
            if self.device == "cuda" and torch.cuda.is_available():
                self.tts = self.tts.to(self.device)
                logger.info("✅ Coqui TTS loaded on GPU")
            else:
                logger.info("✅ Coqui TTS loaded on CPU")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Coqui TTS: {e}")
            # Fallback to a simple model
            try:
                self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
                logger.info("✅ Coqui TTS loaded with fallback model")
            except Exception as e2:
                logger.error(f"❌ TTS initialization completely failed: {e2}")
                raise
    
    def synthesize_to_file(self, text: str, output_path: str, speaker: Optional[str] = None) -> bool:
        """
        Synthesize text to audio file
        
        Args:
            text: Text to synthesize
            output_path: Output audio file path
            speaker: Speaker name (if multi-speaker model)
            
        Returns:
            True if successful
        """
        try:
            if not self.tts:
                logger.error("TTS not initialized")
                return False
            
            logger.info(f"🎵 Synthesizing: {text[:50]}...")
            
            # Generate audio
            if speaker and hasattr(self.tts, 'speakers') and self.tts.speakers:
                self.tts.tts_to_file(text=text, file_path=output_path, speaker=speaker)
            else:
                self.tts.tts_to_file(text=text, file_path=output_path)
            
            logger.info(f"✅ Audio saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ TTS synthesis failed: {e}")
            return False
    
    def synthesize_to_bytes(self, text: str, speaker: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize text to audio bytes
        
        Args:
            text: Text to synthesize
            speaker: Speaker name (if multi-speaker model)
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Synthesize to temporary file
            if self.synthesize_to_file(text, tmp_path, speaker):
                # Read file as bytes
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up temporary file
                Path(tmp_path).unlink(missing_ok=True)
                
                return audio_bytes
            
            return None
            
        except Exception as e:
            logger.error(f"❌ TTS bytes synthesis failed: {e}")
            return None
    
    def get_speakers(self) -> list:
        """Get available speakers (for multi-speaker models)"""
        try:
            if self.tts and hasattr(self.tts, 'speakers') and self.tts.speakers:
                return self.tts.speakers
            return []
        except:
            return []
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "available": COQUI_AVAILABLE,
            "speakers": self.get_speakers(),
            "is_multi_speaker": len(self.get_speakers()) > 0
        }

class OpenSourceTTS:
    """
    Unified Open Source TTS Interface
    Supports Coqui TTS with fallback options
    """
    
    def __init__(self, device: str = "cpu"):
        """Initialize with automatic model selection"""
        self.device = device
        self.tts_engine: Optional[Union[CoquiTTS, Any]] = None
        self.engine_type: Optional[str] = None
        
        # Try to initialize best available TTS
        self._initialize_best_tts()
    
    def _initialize_best_tts(self):
        """Initialize the best available TTS engine"""
        
        # Try Coqui TTS first (best quality)
        if COQUI_AVAILABLE:
            try:
                self.tts_engine = CoquiTTS(device=self.device)
                self.engine_type = "coqui"
                logger.info("✅ Using Coqui TTS (High Quality)")
                return
            except Exception as e:
                logger.warning(f"Coqui TTS failed: {e}")
        
        # Fallback to pyttsx3 (basic but reliable)
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.engine_type = "pyttsx3"
            logger.info("✅ Using pyttsx3 TTS (Basic)")
            return
        except Exception as e:
            logger.warning(f"pyttsx3 TTS failed: {e}")
        
        # Final fallback
        logger.error("❌ No TTS engine available")
        raise RuntimeError("No TTS engine could be initialized")
    
    def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize text to audio bytes
        
        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice/speaker name
            
        Returns:
            Audio bytes or None
        """
        try:
            if self.engine_type == "coqui" and isinstance(self.tts_engine, CoquiTTS):
                return self.tts_engine.synthesize_to_bytes(text, speaker=voice)
            
            elif self.engine_type == "pyttsx3" and self.tts_engine is not None:
                # pyttsx3 synthesis to bytes (requires temporary file)
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                if voice:
                    try:
                        voices = self.tts_engine.getProperty('voices')  # type: ignore
                        if voices:
                            for v in voices:
                                if hasattr(v, 'name') and hasattr(v, 'id') and voice.lower() in v.name.lower():
                                    self.tts_engine.setProperty('voice', v.id)  # type: ignore
                                    break
                    except:
                        pass
                
                try:
                    self.tts_engine.save_to_file(text, tmp_path)  # type: ignore
                    self.tts_engine.runAndWait()  # type: ignore
                except:
                    pass
                
                # Read as bytes
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                Path(tmp_path).unlink(missing_ok=True)
                return audio_bytes
            
            return None
            
        except Exception as e:
            logger.error(f"❌ TTS synthesis failed: {e}")
            return None
    
    def get_info(self) -> dict:
        """Get TTS engine information"""
        info = {
            "engine": self.engine_type,
            "device": self.device,
            "open_source": True,
            "offline": True
        }
        
        if self.engine_type == "coqui" and isinstance(self.tts_engine, CoquiTTS):
            info.update(self.tts_engine.get_model_info())
        
        return info