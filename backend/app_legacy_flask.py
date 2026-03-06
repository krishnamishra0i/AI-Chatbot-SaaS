from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import datetime
import tempfile
import asyncio
import io
import base64
from dotenv import load_dotenv

# Try to import TTS/STT packages upfront for diagnostics
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
    print("[OK] edge-tts imported successfully at startup")
except ImportError as e:
    EDGE_TTS_AVAILABLE = False
    print(f"[ERROR] edge-tts import failed at startup: {e}")

try:
    import whisper
    WHISPER_AVAILABLE = True
    print("[OK] whisper imported successfully at startup")
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"[ERROR] whisper import failed at startup: {e}")

load_dotenv()

app = Flask(__name__)
CORS(app)

# TTS/STT Configuration
TTS_VOICE = os.getenv('TTS_VOICE', 'en-US-GuyNeural')  # Microsoft Edge TTS voice
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')  # tiny, base, small, medium, large

# Lazy load heavy dependencies
_whisper_model = None
_edge_tts_available = EDGE_TTS_AVAILABLE  # Use pre-check result

def get_whisper_model():
    """Lazy load Whisper model for STT"""
    global _whisper_model
    if _whisper_model is None:
        if not WHISPER_AVAILABLE:
            print("[ERROR] Whisper not available - not installed")
            return None
        try:
            _whisper_model = whisper.load_model(WHISPER_MODEL)
            print(f"[OK] Whisper model '{WHISPER_MODEL}' loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load Whisper: {e}")
            return None
    return _whisper_model

def check_edge_tts():
    """Check if edge-tts is available"""
    return EDGE_TTS_AVAILABLE

@app.route('/')
def home():
    return jsonify({
        'message': 'Athena AI Backend API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': str(datetime.datetime.now())
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        # TODO: Integrate with AI/ML service
        response = {
            'message': f'AI Response to: {message}',
            'timestamp': str(datetime.datetime.now())
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# TEXT-TO-SPEECH (TTS) ENDPOINT
# Uses edge-tts (Microsoft Edge's free TTS)
# ============================================
@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using edge-tts
    Request body: { "text": "Hello world", "voice": "en-US-GuyNeural" }
    Returns: audio/mpeg stream or base64 encoded audio
    """
    try:
        # Re-check edge_tts import availability (don't rely on module flag)
        try:
            import edge_tts
        except ImportError:
            return jsonify({'error': 'TTS not available. Install edge-tts: pip install edge-tts'}), 503

        data = request.json or {}
        text = data.get('text', '')
        voice = data.get('voice', TTS_VOICE)
        return_base64 = data.get('base64', False)

        if not text:
            return jsonify({'error': 'text is required'}), 400

        # Run async TTS in sync context
        async def generate_audio():
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b''
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(generate_audio())
        loop.close()

        if return_base64:
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            return jsonify({
                'audio': audio_b64,
                'format': 'mp3',
                'voice': voice
            })
        
        # Return audio file directly
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/mpeg',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tts/voices', methods=['GET'])
def list_tts_voices():
    """List available TTS voices"""
    try:
        # Re-check edge_tts import availability
        try:
            import edge_tts
        except ImportError:
            return jsonify({'error': 'TTS not available'}), 503

        async def get_voices():
            voices = await edge_tts.list_voices()
            return voices

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        voices = loop.run_until_complete(get_voices())
        loop.close()

        # Filter English voices for simplicity
        english_voices = [v for v in voices if v.get('Locale', '').startswith('en-')]
        
        return jsonify({
            'voices': english_voices,
            'default': TTS_VOICE
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# SPEECH-TO-TEXT (STT) ENDPOINT
# Uses OpenAI Whisper (open-source)
# ============================================
@app.route('/api/stt', methods=['POST'])
def speech_to_text():
    """
    Convert speech to text using Whisper
    Request: multipart/form-data with 'audio' file
    Or JSON: { "audio": "<base64-encoded-audio>" }
    Returns: { "text": "transcribed text", "language": "en" }
    """
    try:
        # Re-check whisper import availability
        try:
            import whisper
            model = whisper.load_model(WHISPER_MODEL)
        except ImportError:
            return jsonify({'error': 'STT not available. Install whisper: pip install openai-whisper'}), 503

        # Handle file upload or base64
        audio_file = None
        temp_path = None

        if 'audio' in request.files:
            # File upload
            audio_file = request.files['audio']
            temp_path = tempfile.mktemp(suffix='.wav')
            audio_file.save(temp_path)
        elif request.json and 'audio' in request.json:
            # Base64 encoded audio
            audio_b64 = request.json['audio']
            audio_bytes = base64.b64decode(audio_b64)
            temp_path = tempfile.mktemp(suffix='.wav')
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
        else:
            return jsonify({'error': 'audio file or base64 data required'}), 400

        # Transcribe with Whisper
        result = model.transcribe(temp_path)
        
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'text': result.get('text', '').strip(),
            'language': result.get('language', 'en'),
            'segments': result.get('segments', [])
        })

    except Exception as e:
        # Clean up on error
        if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/stt/info', methods=['GET'])
def stt_info():
    """Get STT service info"""
    model = get_whisper_model()
    return jsonify({
        'available': model is not None,
        'model': WHISPER_MODEL,
        'supported_formats': ['wav', 'mp3', 'ogg', 'flac', 'm4a', 'webm']
    })


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    try:
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')

        # NOTE: This is a mock implementation for development/demo only
        if not email:
            return jsonify({'error': 'email required'}), 400

        # Accept any credentials for demo and return a mock token
        user = {'email': email, 'name': email.split('@')[0]}
        token = f'mock-token-{int(datetime.datetime.now().timestamp())}'
        return jsonify({'user': user, 'token': token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    try:
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'email and password required'}), 400

        # Mock user creation
        user = {'email': email, 'name': email.split('@')[0]}
        token = f'mock-token-{int(datetime.datetime.now().timestamp())}'
        return jsonify({'user': user, 'token': token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/oauth/<provider>')
def auth_oauth(provider):
    # Mock OAuth redirect/callback flow for development.
    # In a real app you'd redirect to the provider and handle callbacks.
    provider = provider.lower()
    if provider not in ('google', 'facebook'):
        return jsonify({'error': 'unsupported provider'}), 400

    user = {'email': f'demo+{provider}@example.com', 'name': f'Demo {provider.title()}'}
    token = f'mock-oauth-{provider}-{int(datetime.datetime.now().timestamp())}'
    return jsonify({'user': user, 'token': token})


@app.route('/api/auth/oauth/google/start')
def google_oauth_start():
    # Build Google OAuth consent URL if client ID configured
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect_base = os.getenv('OAUTH_REDIRECT_BASE', 'http://localhost:5174')
    if not client_id:
        return jsonify({'error': 'GOOGLE_CLIENT_ID not configured'}), 400

    redirect_uri = f"{redirect_base}/oauth-callback/google"
    scope = 'openid email profile'
    state = 'state-demo'
    auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={client_id}&response_type=code&scope={scope}&redirect_uri={redirect_uri}&state={state}&access_type=offline&prompt=consent'
    )
    return jsonify({'auth_url': auth_url})


@app.route('/api/auth/oauth/google/callback')
def google_oauth_callback():
    # Exchange code for token and fetch userinfo if credentials present
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'missing code'}), 400

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_base = os.getenv('OAUTH_REDIRECT_BASE', 'http://localhost:5174')
    redirect_uri = f"{redirect_base}/oauth-callback/google"

    if not client_id or not client_secret:
        # For development, return mock user and token
        user = {'email': f'google-demo@example.com', 'name': 'Google Demo'}
        token = f'mock-oauth-google-{int(datetime.datetime.now().timestamp())}'
        # In a real flow you'd redirect back to frontend with token
        return jsonify({'user': user, 'token': token})

    # Exchange code
    import requests
    token_endpoint = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    token_resp = requests.post(token_endpoint, data=data)
    if token_resp.status_code != 200:
        return jsonify({'error': 'token exchange failed', 'details': token_resp.text}), 400

    tokens = token_resp.json()
    # fetch userinfo
    userinfo = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': f"Bearer {tokens.get('access_token')}"})
    if userinfo.status_code != 200:
        return jsonify({'error': 'userinfo fetch failed', 'details': userinfo.text}), 400

    user = userinfo.json()
    token = tokens.get('access_token')
    return jsonify({'user': user, 'token': token})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
