#!/usr/bin/env python3
"""Standalone test of app module's imports"""
import sys
sys.path.insert(0, r'c:\Krshna\workspace\Ai-Avater-Project\backend')

print("Importing app module...")
from app import EDGE_TTS_AVAILABLE, WHISPER_AVAILABLE, check_edge_tts, get_whisper_model

print(f"EDGE_TTS_AVAILABLE: {EDGE_TTS_AVAILABLE}")
print(f"WHISPER_AVAILABLE: {WHISPER_AVAILABLE}")
print(f"check_edge_tts(): {check_edge_tts()}")
print(f"get_whisper_model(): {get_whisper_model()}")
print("\nModule check passed!")
