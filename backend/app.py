from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

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
