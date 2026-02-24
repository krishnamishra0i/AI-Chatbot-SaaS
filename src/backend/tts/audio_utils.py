"""
Audio utilities for processing and converting audio
"""
import numpy as np
import wave
import io
from typing import Union

class AudioUtils:
    """Audio processing utilities"""
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target dB level
        
        Args:
            audio_data: Audio array
            target_db: Target dB level
            
        Returns:
            Normalized audio array
        """
        # Avoid division by zero
        if np.max(np.abs(audio_data)) == 0:
            return audio_data
        
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Convert to dB
        current_db = 20 * np.log10(rms)
        
        # Calculate scaling factor
        gain_db = target_db - current_db
        gain_linear = 10 ** (gain_db / 20)
        
        return (audio_data * gain_linear).astype(np.float32)
    
    @staticmethod
    def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        Resample audio from one sample rate to another
        
        Args:
            audio_data: Audio array
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio array
        """
        try:
            import librosa
            return librosa.resample(audio_data, orig_sr=orig_sr, target_sr=target_sr)
        except ImportError:
            # Simple resampling fallback
            ratio = target_sr / orig_sr
            new_length = int(len(audio_data) * ratio)
            indices = np.linspace(0, len(audio_data) - 1, new_length)
            return np.interp(indices, np.arange(len(audio_data)), audio_data)
    
    @staticmethod
    def save_wav(audio_data: np.ndarray, filepath: str, sample_rate: int = 16000) -> bool:
        """
        Save audio to WAV file
        
        Args:
            audio_data: Audio array
            filepath: Output file path
            sample_rate: Sample rate
            
        Returns:
            True if successful
        """
        try:
            # Convert to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(filepath, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            return True
        except Exception as e:
            print(f"Error saving WAV file: {e}")
            return False
    
    @staticmethod
    def load_wav(filepath: str) -> tuple:
        """
        Load audio from WAV file
        
        Args:
            filepath: Input file path
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            with wave.open(filepath, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                num_frames = wav_file.getnframes()
                audio_data = wav_file.readframes(num_frames)
                audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32767
            
            return audio_data, sample_rate
        except Exception as e:
            print(f"Error loading WAV file: {e}")
            return None, None
    
    @staticmethod
    def concatenate_audio(*audio_arrays: np.ndarray) -> np.ndarray:
        """Concatenate multiple audio arrays"""
        return np.concatenate(audio_arrays)
    
    @staticmethod
    def add_silence(duration_ms: int, sample_rate: int = 16000) -> np.ndarray:
        """Generate silence"""
        num_samples = int(sample_rate * duration_ms / 1000)
        return np.zeros(num_samples, dtype=np.float32)
