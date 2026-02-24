"""
Voice Activity Detection (VAD) for detecting speech in audio
"""
import numpy as np

class SimpleVAD:
    """Simple Voice Activity Detection using energy threshold"""
    
    def __init__(self, threshold=0.02, frame_duration=0.02, sample_rate=16000):
        """
        Initialize VAD
        
        Args:
            threshold: Energy threshold for speech detection
            frame_duration: Duration of each frame in seconds
            sample_rate: Sample rate of audio
        """
        self.threshold = threshold
        self.frame_duration = frame_duration
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration)
    
    def is_speech(self, audio_chunk):
        """
        Detect if audio chunk contains speech
        
        Args:
            audio_chunk: Audio data (numpy array)
            
        Returns:
            bool: True if speech detected
        """
        if len(audio_chunk) == 0:
            return False
        
        # Normalize audio
        audio_norm = np.abs(audio_chunk)
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_norm ** 2))
        
        return rms > self.threshold
    
    def detect_speech_segments(self, audio_data):
        """
        Detect speech segments in audio
        
        Args:
            audio_data: Full audio data (numpy array)
            
        Returns:
            list: List of (start, end) tuples for speech segments
        """
        segments = []
        in_speech = False
        start = 0
        
        for i in range(0, len(audio_data) - self.frame_size, self.frame_size):
            frame = audio_data[i:i + self.frame_size]
            
            if self.is_speech(frame):
                if not in_speech:
                    start = i
                    in_speech = True
            else:
                if in_speech:
                    segments.append((start, i))
                    in_speech = False
        
        if in_speech:
            segments.append((start, len(audio_data)))
        
        return segments
