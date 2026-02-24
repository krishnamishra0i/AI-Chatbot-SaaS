"""
WebSocket-based real-time streaming speech-to-speech
Streams LLM response word-by-word and TTS audio chunk-by-chunk for zero latency
"""
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
import json
import io
import base64
import concurrent.futures
from typing import Dict, Any

# Module instances
stt_instance = None
llm_instance = None
tts_instance = None

# WebSocket connection
active_connections: list[WebSocket] = []

def set_stt_module(stt):
    global stt_instance
    stt_instance = stt

def set_llm_module(llm):
    global llm_instance
    llm_instance = llm

def set_tts_module(tts):
    global tts_instance
    tts_instance = tts


async def websocket_endpoint(websocket: WebSocket):
    """Real-time streaming speech-to-speech via WebSocket"""
    await websocket.accept()
    active_connections.append(websocket)
    print(f"WebSocket connected: {len(active_connections)} active")
    
    try:
        while True:
            # Receive audio chunk or control message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'audio_chunk':
                # Process audio chunk for transcription
                audio_b64 = message.get('audio', '')
                if audio_b64:
                    audio_data = base64.b64decode(audio_b64)
                    
                    # Transcribe with Whisper
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        result = await loop.run_in_executor(
                            executor,
                            stt_instance.transcribe,
                            audio_data,
                            'en'
                        )
                    transcript = result.get('text', '').strip()
                    
                    if transcript:
                        # Send transcript back
                        await websocket.send_text(json.dumps({
                            'type': 'transcript',
                            'text': transcript
                        }))
                        
                        # Generate LLM response
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            llm_response = await loop.run_in_executor(
                                executor,
                                llm_instance.generate,
                                transcript
                            )
                        response_text = llm_response.get('response', '').strip()
                        
                        if response_text:
                            # Send response text
                            await websocket.send_text(json.dumps({
                                'type': 'llm_chunk',
                                'text': response_text
                            }))
                            
                            # Generate TTS audio
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                tts_audio = await loop.run_in_executor(
                                    executor,
                                    tts_instance.synthesize,
                                    response_text,
                                    'en-US-GuyNeural'
                                )
                            
                            if tts_audio:
                                # Send audio chunk
                                await websocket.send_text(json.dumps({
                                    'type': 'audio_chunk',
                                    'audio': base64.b64encode(tts_audio).decode(),
                                    'format': 'mp3'
                                }))
            
            elif message.get('type') == 'end_speech':
                # Signal end of speech
                await websocket.send_text(json.dumps({'type': 'processing'}))
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {len(active_connections)-1} active")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
