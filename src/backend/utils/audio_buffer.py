"""
Audio buffer management for real-time audio processing
"""
import numpy as np
from collections import deque
from threading import Lock

class AudioBuffer:
    """Thread-safe audio buffer for streaming audio"""
    
    def __init__(self, max_size=160000):
        """
        Initialize audio buffer
        
        Args:
            max_size: Maximum buffer size in samples
        """
        self.buffer = deque(maxlen=max_size)
        self.lock = Lock()
        self.max_size = max_size
    
    def write(self, data):
        """Write audio data to buffer"""
        with self.lock:
            if isinstance(data, np.ndarray):
                self.buffer.extend(data.flatten().tolist())
            else:
                self.buffer.extend(data)
    
    def read(self, size):
        """Read audio data from buffer"""
        with self.lock:
            if len(self.buffer) < size:
                return None
            
            data = []
            for _ in range(size):
                if self.buffer:
                    data.append(self.buffer.popleft())
            
            return np.array(data, dtype=np.float32)
    
    def get_data(self, size):
        """Get audio data without removing from buffer"""
        with self.lock:
            if len(self.buffer) < size:
                return None
            return np.array(list(self.buffer)[:size], dtype=np.float32)
    
    def clear(self):
        """Clear buffer"""
        with self.lock:
            self.buffer.clear()
    
    def size(self):
        """Get current buffer size"""
        with self.lock:
            return len(self.buffer)
