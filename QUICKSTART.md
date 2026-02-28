# Athena AI Avatar Platform - Quick Start Guide

## Prerequisites
- Python 3.13+
- pip (Python package manager)
- Modern web browser (Chrome, Edge, Firefox)

## Installation

### 1. Install Backend Dependencies

```bash
cd backend
python -m pip install -r requirements.txt
```

**Important**: `psycopg2-binary` has been removed from requirements (Windows build issue). If you need PostgreSQL support later, install it separately or use a prebuilt wheel.

### 2. Start the Backend Server

#### Option A: Using the startup script (Recommended)

**Windows (PowerShell):**
```powershell
cd backend
python start_server.py
```

**Windows (CMD):**
```cmd
cd backend
start_server.bat
```

**Linux/macOS:**
```bash
cd backend
python start_server.py
```

#### Option B: Manual Flask command

```bash
cd backend
python -m flask run --no-reload
```

**⚠️ IMPORTANT**: Always use `--no-reload` flag to prevent Flask's watchdog from breaking TTS/STT imports.

Backend will start on: `http://127.0.0.1:5000`

### 3. Start the Frontend Server

Open a new terminal:

```bash
cd frontend
python -m http.server 8000
```

Frontend will be available at: `http://127.0.0.1:8000/athena_complete_platform.html`

## Features Enabled

### ✅ Chat Control Panel
- **Color Presets**: Green, Pink, Orange
- **Toggles**: Enable TTS, Enable STT
- **LLM Selector**: Google / Mock backends
- **Quick Actions**: 
  - Test TTS (plays sample audio)
  - Start/Stop Mic (records and transcribes)

### ✅ TTS (Text-to-Speech)
- Endpoint: `POST /api/tts`
- Uses: Microsoft Edge TTS (open-source)
- Returns: MP3 audio stream or base64

### ✅ STT (Speech-to-Text)
- Endpoint: `POST /api/stt`
- Uses: OpenAI Whisper (open-source, base model)
- Supports: WAV, MP3, OGG, FLAC, M4A, WebM

### ✅ Settings Persistence
- Color preferences saved to localStorage
- TTS/STT/LLM settings persisted across sessions

## Testing Endpoints

### Quick Test Script

```bash
python test_tts_stt.py
```

Expected output:
```
✓ PASS: TTS
✓ PASS: TTS Voices
✓ PASS: STT Info
✓ PASS: STT (FormData upload)
```

### Manual TTS Test

```powershell
$json = @{ text = "Hello from Athena" } | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/tts" -Method POST -Body $json -ContentType "application/json"
# Audio bytes returned in $response.Content
```

## Troubleshooting

### Issue: TTS/STT endpoints return 503 "Not available"

**Solution**: Make sure Flask is running with `--no-reload`:
```bash
python -m flask run --no-reload
```

The watchdog reloader breaks Python imports. Using `--no-reload` fixes this.

### Issue: Microphone not working in browser

**Solution**: 
1. Enable microphone permissions in browser
2. Check that `mediaDevices.getUserMedia` is supported
3. Use HTTPS in production (required by browser security)

### Issue: Audio playback has issues

**Solution**:
1. Check browser audio settings
2. Test audio with different voices via `/api/tts/voices` endpoint
3. Try different browsers

## Project Structure

```
Ai-Avater-Project/
├── backend/
│   ├── app.py                 # Flask backend with TTS/STT endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── start_server.py        # Startup script (Python)
│   └── start_server.bat       # Startup script (Windows CMD)
├── frontend/
│   ├── athena_complete_platform.html  # Main SPA with Chat Control Panel
│   ├── react-app/             # Vite + React alternative
│   └── react-frontend/        # Create React App version
├── test_tts_stt.py           # Endpoint test suite
└── test_app_imports.py        # Module import diagnostics
```

## Environment Variables (Optional)

Create a `.env` file in the `backend/` directory:

```env
TTS_VOICE=en-US-GuyNeural
WHISPER_MODEL=base
FLASK_ENV=production
FLASK_DEBUG=0
```

## Next Steps

1. **Customize**: Modify `PAUL_SYSTEM_PROMPT` in [athena_complete_platform.html](frontend/athena_complete_platform.html#L2401) to change AI personality
2. **Integrate LLM**: Wire the `/api/chat` endpoint to actual AI backend (currently mock)
3. **Production**: Use Gunicorn for production deployment instead of Flask dev server
4. **Styling**: Adjust CSS variables (`--accent-green`, `--accent-pink`, etc.) for custom branding

## Performance Notes

- Whisper model (~140MB) is lazy-loaded on first STT request
- TTS uses cloud-based Microsoft Edge service (requires internet)
- Recommend at least 2GB free RAM for Whisper operations
- For large-scale deployments, consider:
  - Using Gunicorn with multiple workers
  - Deploying Whisper separately (slower first transcription)
  - Caching TTS outputs for common phrases

---

**Last Updated**: March 1, 2026
