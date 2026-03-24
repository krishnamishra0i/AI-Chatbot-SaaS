"""
Real-time Audio Streaming Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Handles real-time audio streaming with:
- Audio chunking & buffering
- Concurrent STT/TTS processing
- WebSocket support
- Streaming audio formats (WAV, OPUS)
- Low-latency processing
"""

import asyncio
import io
import struct
import base64
from typing import AsyncGenerator, Optional
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio streaming configuration."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 2048  # 128ms at 16kHz
    format: str = "wav"  # wav, opus, pcm
    encoding: str = "pcm16"
    buffer_duration_seconds: float = 1.0


class AudioBuffer:
    """Thread-safe audio buffer for streaming."""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.buffer = deque(maxlen=int(config.sample_rate * config.buffer_duration_seconds // config.chunk_size))
        self.lock = asyncio.Lock()
        self.has_data = asyncio.Event()
    
    async def append(self, audio_chunk: bytes):
        """Add audio chunk to buffer."""
        async with self.lock:
            self.buffer.append(audio_chunk)
            self.has_data.set()
    
    async def get_chunk(self) -> Optional[bytes]:
        """Get next audio chunk."""
        async with self.lock:
            if not self.buffer:
                return None
            return self.buffer.popleft()
    
    async def wait_for_data(self, timeout: float = 5.0) -> bool:
        """Wait for audio data with timeout."""
        try:
            self.has_data.clear()
            await asyncio.wait_for(self.has_data.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False
    
    async def flush(self):
        """Clear buffer."""
        async with self.lock:
            self.buffer.clear()


class RealtimeAudioStreamer:
    """Real-time audio streaming handler."""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.buffer = AudioBuffer(self.config)
        self.is_streaming = False
    
    async def stream_audio_chunks(
        self, 
        audio_data: bytes
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio in chunks for real-time processing.
        
        Args:
            audio_data: Complete audio blob
        
        Yields:
            Audio chunks optimized for STT streaming
        """
        offset = 0
        while offset < len(audio_data):
            chunk = audio_data[offset:offset + self.config.chunk_size]
            if chunk:
                yield chunk
            offset += self.config.chunk_size
            # Small delay to avoid overwhelming receiver
            await asyncio.sleep(0.01)
    
    async def stream_audio_from_buffer(
        self,
        duration: float = 60.0,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks from buffer (WebSocket listening).
        
        Args:
            duration: Maximum streaming duration in seconds
        
        Yields:
            Audio chunks from realtime buffer
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            chunk = await self.buffer.get_chunk()
            
            if chunk:
                yield chunk
            else:
                # Wait for more data
                has_data = await self.buffer.wait_for_data(timeout=0.5)
                if not has_data:
                    # Timeout - check if still should stream
                    if not self.is_streaming:
                        break
    
    def convert_audio_format(
        self,
        audio_bytes: bytes,
        from_format: str = "wav",
        to_format: str = "pcm16",
    ) -> bytes:
        """
        Convert between audio formats.
        
        Args:
            audio_bytes: Audio data
            from_format: Source format (wav, webm, mp3, pcm16)
            to_format: Target format (wav, pcm16, opus)
        
        Returns:
            Converted audio bytes
        """
        try:
            if from_format == "wav" and to_format == "pcm16":
                # Extract PCM from WAV
                if len(audio_bytes) < 44:  # WAV header minimum
                    return audio_bytes
                # Skip WAV header (44 bytes)
                return audio_bytes[44:]
            
            elif from_format == "webm" and to_format == "pcm16":
                # WebM contains opus codec, typically 16kHz sampled
                # For now, return as-is (proper conversion needs ffmpeg)
                return audio_bytes
            
            return audio_bytes
        except Exception as e:
            logger.error(f"Audio format conversion failed: {e}")
            return audio_bytes
    
    def encode_audio_chunk(
        self,
        chunk: bytes,
        encoding: str = "base64"
    ) -> str:
        """
        Encode audio chunk for transmission.
        
        Args:
            chunk: Raw audio bytes
            encoding: Encoding type (base64, hex)
        
        Returns:
            Encoded audio string
        """
        if encoding == "base64":
            return base64.b64encode(chunk).decode("utf-8")
        elif encoding == "hex":
            return chunk.hex()
        return base64.b64encode(chunk).decode("utf-8")
    
    def decode_audio_chunk(
        self,
        encoded: str,
        encoding: str = "base64"
    ) -> bytes:
        """
        Decode audio chunk from transmission.
        
        Args:
            encoded: Encoded audio string
            encoding: Encoding type (base64, hex)
        
        Returns:
            Raw audio bytes
        """
        try:
            if encoding == "base64":
                return base64.b64decode(encoded)
            elif encoding == "hex":
                return bytes.fromhex(encoded)
            return base64.b64decode(encoded)
        except Exception as e:
            logger.error(f"Audio decoding failed: {e}")
            return b""
    
    async def collect_audio_stream(
        self,
        chunk_generator: AsyncGenerator,
        max_duration: float = 60.0,
    ) -> bytes:
        """
        Collect streaming audio chunks into single buffer.
        
        Args:
            chunk_generator: Async generator yielding audio chunks
            max_duration: Maximum collection duration
        
        Returns:
            Complete audio bytes
        """
        audio_buffer = io.BytesIO()
        start_time = asyncio.get_event_loop().time()
        
        try:
            async for chunk in chunk_generator:
                if (asyncio.get_event_loop().time() - start_time) > max_duration:
                    break
                
                if chunk:
                    audio_buffer.write(chunk)
            
            return audio_buffer.getvalue()
        finally:
            audio_buffer.close()
    
    def estimate_duration(self, audio_bytes: bytes) -> float:
        """
        Estimate audio duration in seconds.
        
        Args:
            audio_bytes: Audio data
        
        Returns:
            Duration in seconds
        """
        # Standard: 16-bit mono at 16kHz = 2 bytes per sample
        # Duration = bytes / (sample_rate * bytes_per_sample)
        bytes_per_second = self.config.sample_rate * 2
        return len(audio_bytes) / bytes_per_second if bytes_per_second > 0 else 0


# Global instance
_streamer = None


def get_streamer(config: Optional[AudioConfig] = None) -> RealtimeAudioStreamer:
    """Get or create global streamer instance."""
    global _streamer
    if _streamer is None:
        _streamer = RealtimeAudioStreamer(config or AudioConfig())
    return _streamer
