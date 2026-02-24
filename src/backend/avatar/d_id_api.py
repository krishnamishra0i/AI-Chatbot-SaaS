"""
D-ID API Integration for real-time animated avatars
"""
import os
import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DIDAvatar:
    """D-ID API client for creating talking avatar videos"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("D_ID_API_KEY")
        self.api_url = os.getenv("D_ID_API_URL", "https://api.d-id.com")
        self.timeout = aiohttp.ClientTimeout(total=300)
        
        if not self.api_key:
            logger.warning("D-ID API key not configured. Set D_ID_API_KEY environment variable.")
    
    async def create_talking_video(
        self,
        text: str,
        image_url: str,
        voice_id: str = "en_US-Neural2-C",
        result_format: str = "mp4"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a talking video using D-ID API
        
        Args:
            text: Text to speak
            image_url: URL or path to avatar image
            voice_id: Voice model ID
            result_format: Output format (mp4, webm, etc)
        
        Returns:
            Dictionary with video details or None if failed
        """
        if not self.api_key:
            logger.error("D-ID API key not configured")
            return None
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "google",
                    "voice_id": voice_id
                },
                "input": text
            },
            "source_url": image_url,
            "config": {
                "fluent": True,
                "pad_audio": 0
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.api_url}/talks",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"✅ D-ID video created: {result.get('id')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"D-ID API error ({response.status}): {error_text}")
                        return None
        except Exception as e:
            logger.error(f"D-ID API request failed: {e}")
            return None
    
    async def get_video_status(self, talk_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a created video"""
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Basic {self.api_key}"
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.api_url}/talks/{talk_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get video status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to check video status: {e}")
            return None
    
    async def stream_video_generation(
        self,
        text: str,
        image_url: str,
        voice_id: str = "en_US-Neural2-C"
    ):
        """
        Stream video generation status until complete
        
        Yields status updates while video is being generated
        """
        # Create the video
        result = await self.create_talking_video(
            text=text,
            image_url=image_url,
            voice_id=voice_id
        )
        
        if not result:
            yield {
                "status": "error",
                "message": "Failed to create video"
            }
            return
        
        talk_id = result.get("id")
        yield {
            "status": "created",
            "talk_id": talk_id,
            "message": "Video generation started"
        }
        
        # Poll for completion
        max_attempts = 120  # 2 minutes with 1-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            status = await self.get_video_status(talk_id)
            
            if not status:
                await asyncio.sleep(1)
                attempt += 1
                continue
            
            state = status.get("status")
            
            if state == "done":
                yield {
                    "status": "done",
                    "talk_id": talk_id,
                    "video_url": status.get("result_url"),
                    "duration": status.get("duration"),
                    "message": "Video generation complete"
                }
                return
            elif state == "failed":
                yield {
                    "status": "failed",
                    "talk_id": talk_id,
                    "error": status.get("error"),
                    "message": "Video generation failed"
                }
                return
            elif state == "pending" or state == "processing":
                yield {
                    "status": "processing",
                    "talk_id": talk_id,
                    "progress": "Video is being generated...",
                    "message": f"Status: {state}"
                }
            
            await asyncio.sleep(1)
            attempt += 1
        
        yield {
            "status": "timeout",
            "talk_id": talk_id,
            "message": "Video generation timeout"
        }


# Global instance
_did_client: Optional[DIDAvatar] = None


def get_did_client() -> Optional[DIDAvatar]:
    """Get or create D-ID client"""
    global _did_client
    if _did_client is None:
        _did_client = DIDAvatar()
    return _did_client


def set_did_client(client: DIDAvatar):
    """Set D-ID client instance"""
    global _did_client
    _did_client = client
