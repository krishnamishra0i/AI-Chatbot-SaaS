#!/usr/bin/env python3
"""Quick test of TTS and STT endpoints."""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_tts():
    """Test TTS endpoint."""
    print("\n=== Testing TTS ===")
    try:
        payload = {'text': 'Hello from Athena. This is a test of the text to speech system.'}
        resp = requests.post(f'{BASE_URL}/api/tts', json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"✓ TTS succeeded: received {len(resp.content)} bytes of audio")
            # Save sample audio for manual testing
            with open('test_audio.wav', 'wb') as f:
                f.write(resp.content)
            print("  Saved to test_audio.wav")
            return True
        else:
            print(f"✗ TTS failed with status {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ TTS error: {e}")
        return False

def test_tts_voices():
    """Test TTS voices endpoint."""
    print("\n=== Testing TTS Voices ===")
    try:
        resp = requests.get(f'{BASE_URL}/api/tts/voices', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ TTS voices endpoint succeeded: {len(data)} voices available")
            if isinstance(data, list) and len(data) > 0:
                print(f"  Sample: {data[0]}")
            return True
        else:
            print(f"✗ TTS voices failed with status {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ TTS voices error: {e}")
        return False

def test_stt_info():
    """Test STT info endpoint."""
    print("\n=== Testing STT Info ===")
    try:
        resp = requests.get(f'{BASE_URL}/api/stt/info', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ STT info endpoint succeeded:")
            print(f"  {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ STT info failed with status {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ STT info error: {e}")
        return False

def test_stt_with_file():
    """Test STT with a simple audio file (if available)."""
    print("\n=== Testing STT (with FormData upload) ===")
    try:
        # Create a minimal WAV file (silence, 1 second at 16kHz)
        import struct
        sample_rate = 16000
        duration = 1  # 1 second of silence
        silence = b'\x00\x00' * (sample_rate * duration)
        
        # WAV header for mono 16-bit PCM
        num_samples = len(silence) // 2
        byte_rate = sample_rate * 2
        wav = (
            b'RIFF' + struct.pack('<I', 36 + len(silence)) +
            b'WAVE' +
            b'fmt ' + struct.pack('<I', 16) +  # fmt chunk size
            struct.pack('<HHIIHH', 1, 1, sample_rate, byte_rate, 2, 16) +
            b'data' + struct.pack('<I', len(silence)) +
            silence
        )
        
        # Send as multipart/form-data (file upload)
        import io
        files = {'audio': ('test.wav', io.BytesIO(wav), 'audio/wav')}
        resp = requests.post(f'{BASE_URL}/api/stt', files=files, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ STT succeeded: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ STT failed with status {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ STT error: {e}")
        return False

if __name__ == '__main__':
    print("Testing Athena TTS/STT Endpoints")
    print("=" * 40)
    
    results = {
        'TTS': test_tts(),
        'TTS Voices': test_tts_voices(),
        'STT Info': test_stt_info(),
        'STT (base64)': test_stt_with_file(),
    }
    
    print("\n" + "=" * 40)
    print("Summary:")
    for test_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_pass = all(results.values())
    print(f"\nOverall: {'✓ All tests passed!' if all_pass else '✗ Some tests failed'}")
