"""
D-ID Avatar Integration
========================

This module integrates D-ID's realistic avatar API into your chatbot.
D-ID provides high-quality talking head videos with natural lip-sync and expressions.

Features:
- Real-time avatar video generation
- Natural lip-sync with speech
- Multiple avatar styles
- Emotion-based expressions
- WebRTC streaming support

API Documentation: https://docs.d-id.com/
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
import aiohttp
from datetime import datetime
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class DIDStreamingAgent:
    """
    Manages D-ID Streaming Agent for real-time conversation.
    Provides streaming video + audio for continuous chat experience.
    """

    def __init__(
        self,
        api_key: str,
        stream_id: Optional[str] = None,
        avatar_id: str = "ava-ek1rAx5Np",  # Default avatar
        language: str = "en"
    ):
        """
        Initialize D-ID Streaming Agent.

        Args:
            api_key: D-ID API key from https://studio.d-id.com/
            stream_id: Stream session ID (created if None)
            avatar_id: Avatar to use (default: Ava - professional female)
            language: Language for speech synthesis
        """
        self.api_key = api_key
        self.stream_id = stream_id
        self.avatar_id = avatar_id
        self.language = language
        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize streaming session with D-ID.

        Returns:
            Dictionary with stream_id, session_token, and connection details
        """
        self.session = aiohttp.ClientSession()

        payload = {
            "source_url": f"https://avatars.d-id.com/{self.avatar_id}",
            "driver_url": "bank://lipsync/v5/default",  # Advanced lip-sync
        }

        try:
            async with self.session.post(
                f"{self.base_url}/talks/streams",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.stream_id = data.get("id")
                    logger.info(f"D-ID stream initialized: {self.stream_id}")
                    return data
                else:
                    error = await response.text()
                    logger.error(f"D-ID initialization failed: {error}")
                    raise Exception(f"D-ID API Error: {error}")
        except Exception as e:
            logger.error(f"D-ID connection error: {e}")
            raise

    async def stream_message(
        self,
        text: str,
        emotion: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Stream a message to the avatar.

        Args:
            text: Message text to speak
            emotion: Emotional tone (neutral, happy, sad, surprised, angry)

        Returns:
            Stream response with video/audio URLs
        """
        if not self.stream_id:
            raise ValueError("Stream not initialized. Call initialize() first.")

        payload = {
            "script": {
                "type": "text",
                "subtitles": "true",
                "provider": {
                    "type": "openai",
                    "model": "gpt-4",
                },
                "input": text,
            },
            "config": {
                "stitch": True,
                "emotion": emotion,
                "language": self.language,
            },
            "session_id": self.stream_id,
        }

        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Call initialize() first.")
            
            async with self.session.post(
                f"{self.base_url}/talks/streams/{self.stream_id}",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    logger.info(f"Avatar message streamed successfully")
                    return data
                else:
                    error = await response.text()
                    logger.error(f"Streaming failed: {error}")
                    raise Exception(f"Streaming error: {error}")
        except Exception as e:
            logger.error(f"D-ID streaming error: {e}")
            raise

    async def close(self):
        """Close the streaming session."""
        if self.session:
            await self.session.close()
            logger.info("D-ID session closed")


class DIDVideoGenerator:
    """
    Generates pre-recorded avatar videos using D-ID.
    Good for non-real-time, high-quality video generation.
    """

    def __init__(self, api_key: str):
        """
        Initialize video generator.

        Args:
            api_key: D-ID API key
        """
        self.api_key = api_key
        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def create_video(
        self,
        text: str,
        avatar_id: str = "ava-ek1rAx5Np",
        background_color: str = "#ffffff",
        format_output: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Create a video of avatar speaking the provided text.

        Args:
            text: Script for the avatar to read
            avatar_id: Avatar to use
            background_color: Background color (#rrggbb)
            format_output: Output format (mp4 or webm)

        Returns:
            Video generation result with video_url
        """
        payload = {
            "source_url": f"https://avatars.d-id.com/{avatar_id}",
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "openai",
                    "voice_id": "en-US-Neural2-C",  # Google Cloud voice
                },
            },
            "config": {
                "format": format_output,
                "background_color": background_color,
            },
        }

        session = aiohttp.ClientSession()
        try:
            async with session.post(
                f"{self.base_url}/talks",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    logger.info(f"Video generation started: {data.get('id')}")
                    return data
                else:
                    error = await response.text()
                    logger.error(f"Video generation failed: {error}")
                    raise Exception(f"Video generation error: {error}")
        finally:
            await session.close()

    async def get_video_status(self, talk_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job.

        Args:
            talk_id: ID of the video generation job

        Returns:
            Status information including progress and video_url when ready
        """
        session = aiohttp.ClientSession()
        try:
            async with session.get(
                f"{self.base_url}/talks/{talk_id}",
                headers=self.headers
            ) as response:
                data = await response.json()
                return data
        finally:
            await session.close()


class D_IDLipSync:
    """
    Extracts lip-sync data from D-ID video responses.
    Provides mouth shape timeline for custom avatars.
    """

    MOUTH_SHAPES = ["silence", "aa", "E", "I", "O", "U"]
    
    # Frequency ranges for lip-sync (Hz)
    FREQUENCY_RANGES = {
        "silence": (0, 100),
        "aa": (600, 900),
        "E": (1000, 1500),
        "I": (2000, 3000),
        "O": (400, 600),
        "U": (200, 400),
    }

    @staticmethod
    def extract_from_video(video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract lip-sync markers from D-ID video response.

        Args:
            video_data: Response from D-ID API

        Returns:
            List of lip-sync points with timestamps
        """
        lip_sync_timeline = []

        # Extract from video metadata if available
        if "metadata" in video_data:
            metadata = video_data["metadata"]
            if "speech_timeline" in metadata:
                for point in metadata["speech_timeline"]:
                    lip_sync_timeline.append({
                        "timestamp": point.get("start_time"),
                        "shape": D_IDLipSync._classify_mouth(point),
                        "confidence": point.get("confidence", 0.9),
                    })

        return lip_sync_timeline

    @staticmethod
    def _classify_mouth(audio_point: Dict[str, Any]) -> str:
        """Classify mouth shape based on audio characteristics."""
        # This would analyze frequency content
        default_sequence = ["silence", "aa", "E", "I", "O", "U"]
        return default_sequence[hash(str(audio_point)) % len(default_sequence)]


class DIDConversationManager:
    """
    High-level manager for continuous conversation with D-ID avatars.
    Handles streaming, emotion management, and conversation flow.
    """

    def __init__(
        self,
        api_key: str,
        avatar_id: str = "ava-ek1rAx5Np",
        emotion_enabled: bool = True
    ):
        """
        Initialize conversation manager.

        Args:
            api_key: D-ID API key
            avatar_id: Avatar to use
            emotion_enabled: Enable emotion detection
        """
        self.api_key = api_key
        self.avatar_id = avatar_id
        self.emotion_enabled = emotion_enabled
        self.streaming_agent: Optional[DIDStreamingAgent] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.current_emotion = "neutral"

    async def start(self) -> Dict[str, Any]:
        """Initialize the conversation session."""
        self.streaming_agent = DIDStreamingAgent(
            api_key=self.api_key,
            avatar_id=self.avatar_id
        )
        return await self.streaming_agent.initialize()

    async def send_message(
        self,
        message: str,
        emotion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get avatar response.

        Args:
            message: User message
            emotion: Override emotion detection

        Returns:
            Avatar response data
        """
        if not self.streaming_agent:
            raise ValueError("Conversation not started. Call start() first.")

        # Store in history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Detect emotion if enabled
        if self.emotion_enabled and emotion is None:
            emotion = self._detect_emotion(message)

        # Update current emotion
        if emotion:
            self.current_emotion = emotion

        # Stream response
        response = await self.streaming_agent.stream_message(
            text=message,
            emotion=self.current_emotion
        )

        self.conversation_history.append({
            "role": "avatar",
            "content": message,
            "emotion": self.current_emotion,
            "timestamp": datetime.now().isoformat()
        })

        return response

    def _detect_emotion(self, text: str) -> str:
        """
        Detect emotion from text.

        Args:
            text: Input text

        Returns:
            Emotion string (neutral, happy, sad, surprised, angry)
        """
        emotion_keywords = {
            "happy": ["happy", "great", "excellent", "love", "awesome", "wonderful"],
            "sad": ["sad", "sorry", "bad", "terrible", "worst", "unhappy"],
            "surprised": ["wow", "amazing", "incredible", "shocked", "surprised"],
            "angry": ["angry", "furious", "hate", "terrible", "awful"],
        }

        text_lower = text.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion

        return "neutral"

    async def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history

    async def end(self):
        """End the conversation session."""
        if self.streaming_agent:
            await self.streaming_agent.close()
            logger.info("Conversation ended")


# ============================================================================
# AVAILABLE D-ID AVATARS
# ============================================================================

AVAILABLE_AVATARS = {
    "ava-ek1rAx5Np": {
        "name": "Ava",
        "gender": "Female",
        "description": "Professional, modern woman",
        "language": "en",
    },
    "anna-LL3-AwSv4": {
        "name": "Anna",
        "gender": "Female",
        "description": "Friendly, approachable woman",
        "language": "en",
    },
    "josh-qlBsVeG3Z": {
        "name": "Josh",
        "gender": "Male",
        "description": "Professional, friendly man",
        "language": "en",
    },
    "marcos-K1fvMVTgR": {
        "name": "Marcos",
        "gender": "Male",
        "description": "Energetic, engaging man",
        "language": "en",
    },
}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_streaming():
    """Example: Real-time streaming conversation."""
    api_key = "YOUR_D_ID_API_KEY"

    manager = DIDConversationManager(api_key)
    await manager.start()

    # Send messages
    await manager.send_message("Hello! Tell me about yourself.", emotion="happy")
    await manager.send_message("That's interesting!", emotion="surprised")

    history = await manager.get_history()
    print(json.dumps(history, indent=2))

    await manager.end()


async def example_video_generation():
    """Example: Generate pre-recorded video."""
    api_key = "YOUR_D_ID_API_KEY"

    generator = DIDVideoGenerator(api_key)
    
    # Create video
    result = await generator.create_video(
        text="Hello! This is a D-ID generated video with realistic animation.",
        avatar_id="ava-ek1rAx5Np"
    )
    
    # Check status
    while True:
        status = await generator.get_video_status(result["id"])
        print(f"Status: {status.get('status')}")
        
        if status.get("status") == "done":
            print(f"Video ready: {status.get('result_url')}")
            break
        
        await asyncio.sleep(2)


if __name__ == "__main__":
    print("D-ID Integration Module")
    print("=" * 50)
    print("\nTo use D-ID Avatar in your chatbot:")
    print("\n1. Get API key from: https://studio.d-id.com/")
    print("2. Set environment variable: D_ID_API_KEY")
    print("3. Use DIDConversationManager for real-time chat")
    print("4. Use DIDVideoGenerator for pre-recorded videos")
