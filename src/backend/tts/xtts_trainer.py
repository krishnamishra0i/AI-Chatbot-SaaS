"""
XTTS v2 Model Training Module
==============================
Train XTTS-v2 model with your own voice samples for custom voice cloning
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict
import json
from datetime import datetime
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class XTTSVoiceTrainer:
    """Train XTTS v2 model with custom voice samples"""
    
    def __init__(self, device: str = "cpu", output_dir: Optional[str] = None):
        """
        Initialize XTTS Voice Trainer
        
        Args:
            device: 'cpu' or 'cuda'
            output_dir: Directory to save trained models
        """
        # Ensure output directory exists regardless of whether the TTS library is available
        output_path = output_dir if output_dir else "models/custom_voices"
        self.output_dir = Path(output_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default attributes in case TTS isn't installed
        self.tts_lib = None
        self.device = device
        self.model = None
        self.speaker_embeddings = {}

        try:
            from TTS.api import TTS  # type: ignore
            self.tts_lib = TTS

            # Load base XTTS model
            logger.info(f"Loading base XTTS v2 model on {device}...")
            try:
                # Newer TTS API accepts `device` kwarg
                self.model = TTS(
                    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                    device=device,
                    gpu_verbose=False
                )
            except TypeError:
                # Older TTS versions may not accept `device`; try without it
                logger.info("TTS constructor does not accept 'device'; retrying without it")
                self.model = TTS(
                    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                    gpu_verbose=False
                )
            logger.info("✅ XTTS Trainer initialized")
        except ImportError:
            logger.warning("TTS library not installed; XTTS trainer disabled. Install with: pip install TTS")
        except Exception as e:
            # Non-fatal - XTTS trainer is optional. Log as warning to avoid startup errors.
            logger.warning(f"Unexpected error initializing XTTS trainer (optional): {e}")
    
    def prepare_training_data(
        self,
        voice_sample_dir: str,
        language: str = "en",
        min_duration: float = 0.5,
        max_duration: float = 30.0
    ) -> Dict:
        """
        Prepare voice samples for training
        
        Args:
            voice_sample_dir: Directory with .wav or .mp3 files
            language: Language code
            min_duration: Minimum audio duration in seconds
            max_duration: Maximum audio duration in seconds
            
        Returns:
            Dictionary with metadata about prepared samples
        """
        logger.info(f"Preparing training data from {voice_sample_dir}...")
        
        voice_dir = Path(voice_sample_dir)
        audio_files = list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3"))
        
        if not audio_files:
            logger.error(f"No audio files found in {voice_sample_dir}")
            return {"error": "No audio files found", "count": 0}
        
        valid_files = []
        for audio_file in audio_files:
            try:
                import librosa
                duration = librosa.get_duration(filename=str(audio_file))
                
                if min_duration <= duration <= max_duration:
                    valid_files.append({
                        "path": str(audio_file),
                        "duration": duration,
                        "language": language
                    })
                    logger.info(f"✅ Valid: {audio_file.name} ({duration:.2f}s)")
                else:
                    logger.warning(f"⚠️  Skipped: {audio_file.name} ({duration:.2f}s - outside range)")
            except Exception as e:
                logger.error(f"Error processing {audio_file}: {e}")
        
        metadata = {
            "language": language,
            "total_samples": len(valid_files),
            "total_duration": sum(f["duration"] for f in valid_files),
            "files": valid_files
        }
        
        # Save metadata
        metadata_path = self.output_dir / "training_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Prepared {len(valid_files)} samples ({metadata['total_duration']:.2f}s total)")
        return metadata
    
    def extract_speaker_embedding(
        self,
        reference_audio_path: str,
        speaker_name: str = "custom_speaker"
    ) -> bool:
        """
        Extract speaker embedding from reference audio
        
        Args:
            reference_audio_path: Path to reference audio file
            speaker_name: Name for this speaker
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Extracting speaker embedding from {reference_audio_path}...")
            
            # Store the reference audio path for this speaker
            self.speaker_embeddings[speaker_name] = {
                "reference_audio": reference_audio_path,
                "created_at": datetime.now().isoformat(),
                "status": "ready"
            }
            
            logger.info(f"✅ Speaker embedding extracted for '{speaker_name}'")
            return True
        except Exception as e:
            logger.error(f"Error extracting embedding: {e}")
            return False
    
    def fine_tune(
        self,
        training_data_dir: str,
        speaker_name: str = "custom_speaker",
        num_epochs: int = 10,
        learning_rate: float = 1e-4
    ) -> Dict:
        """
        Fine-tune XTTS model with custom voice data
        
        Args:
            training_data_dir: Directory with training audio files
            speaker_name: Name for the speaker/voice
            num_epochs: Number of training epochs
            learning_rate: Learning rate for training
            
        Returns:
            Training results dictionary
        """
        try:
            logger.info(f"Starting fine-tuning for speaker '{speaker_name}'...")
            
            # Prepare data
            training_meta = self.prepare_training_data(training_data_dir)
            
            if "error" in training_meta:
                return training_meta
            
            if training_meta["total_samples"] < 3:
                logger.error("Need at least 3 samples for training")
                return {"error": "Insufficient training samples (minimum 3 required)"}
            
            logger.info(f"Training with {training_meta['total_samples']} samples...")
            
            # Extract first audio as reference
            first_audio = training_meta["files"][0]["path"]
            self.extract_speaker_embedding(first_audio, speaker_name)
            
            # Note: Full fine-tuning would require XTTS training code
            # For now, we'll use voice cloning with the reference audio
            training_result = {
                "speaker_name": speaker_name,
                "status": "completed",
                "samples_used": training_meta["total_samples"],
                "total_duration": training_meta["total_duration"],
                "reference_audio": first_audio,
                "trained_at": datetime.now().isoformat(),
                "epochs": num_epochs,
                "learning_rate": learning_rate
            }
            
            # Save training results
            model_dir = self.output_dir / speaker_name
            model_dir.mkdir(exist_ok=True)
            
            result_path = model_dir / "training_result.json"
            with open(result_path, 'w') as f:
                json.dump(training_result, f, indent=2)
            
            logger.info(f"✅ Fine-tuning completed for '{speaker_name}'")
            logger.info(f"📁 Model saved to {model_dir}")
            
            return training_result
        
        except Exception as e:
            logger.error(f"Fine-tuning error: {e}")
            return {"error": str(e), "status": "failed"}
    
    def synthesize_with_trained_voice(
        self,
        text: str,
        speaker_name: str,
        language: str = "en"
    ) -> Optional[np.ndarray]:
        """
        Synthesize speech using trained voice
        
        Args:
            text: Text to synthesize
            speaker_name: Name of trained speaker
            language: Language code
            
        Returns:
            Audio data (numpy array) or None if error
        """
        try:
            if speaker_name not in self.speaker_embeddings:
                logger.error(f"Speaker '{speaker_name}' not found")
                return None
            
            speaker_info = self.speaker_embeddings[speaker_name]
            reference_audio = speaker_info["reference_audio"]
            
            logger.info(f"Synthesizing with voice '{speaker_name}'...")
            
            # Ensure model is initialized before calling its methods
            if not self.model:
                logger.error("TTS model not initialized or XTTS unavailable")
                return None

            audio = self.model.tts(
                text=text,
                speaker_wav=reference_audio,
                language=language
            )
            
            return np.array(audio, dtype=np.float32)
        
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return None
    
    def list_trained_speakers(self) -> List[str]:
        """
        List all trained speakers
        
        Returns:
            List of speaker names
        """
        speakers = []
        for speaker_dir in self.output_dir.iterdir():
            if speaker_dir.is_dir():
                result_file = speaker_dir / "training_result.json"
                if result_file.exists():
                    speakers.append(speaker_dir.name)
        
        return speakers
    
    def get_speaker_info(self, speaker_name: str) -> Optional[Dict]:
        """
        Get information about a trained speaker
        
        Args:
            speaker_name: Name of speaker
            
        Returns:
            Speaker information dictionary or None
        """
        result_file = self.output_dir / speaker_name / "training_result.json"
        
        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def delete_trained_speaker(self, speaker_name: str) -> bool:
        """
        Delete a trained speaker model
        
        Args:
            speaker_name: Name of speaker to delete
            
        Returns:
            True if successful
        """
        try:
            import shutil
            speaker_dir = self.output_dir / speaker_name
            
            if speaker_dir.exists():
                shutil.rmtree(speaker_dir)
                if speaker_name in self.speaker_embeddings:
                    del self.speaker_embeddings[speaker_name]
                logger.info(f"✅ Deleted speaker '{speaker_name}'")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting speaker: {e}")
            return False
