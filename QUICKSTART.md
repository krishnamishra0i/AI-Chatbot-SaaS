# Athena AI Avatar Platform - Quick Start Guide

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Modern web browser (Chrome, Edge, Firefox)

## Installation

### 1. Install Backend Dependencies

```bash
cd backend
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example env file and configure your API keys:

```bash
cd backend
copy .env.example .env
```

Edit `.env` with your settings:
```env
# Required for AI chat (at least one)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Optional: Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Optional: Custom settings
SECRET_KEY=your-secret-key
TTS_VOICE=en-US-GuyNeural
WHISPER_MODEL=base
```

> If no LLM API keys are set, the chat will use a mock AI backend.

### 3. Start the Backend Server

```bash
cd backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload
```

Backend will start on: `http://localhost:5000`

- API docs: `http://localhost:5000/docs` (Swagger UI)
- Health check: `http://localhost:5000/api/health`

### 4. Start the React Frontend

Open a new terminal:

```bash
cd react-frontend
npm install   # first time only
npm start
```

Frontend will be available at: `http://localhost:3000`

> The frontend proxies API requests to `http://localhost:5000` in development mode.

## Architecture

```
AI-Chatbot-SaaS/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app entry point (42 routes)
│   │   ├── core/
│   │   │   ├── config.py        # Environment configuration
│   │   │   ├── database.py      # SQLAlchemy async + aiosqlite
│   │   │   └── security.py      # JWT + bcrypt auth
│   │   ├── models/
│   │   │   └── models.py        # DB models (User, Chatbot, ApiKey, etc.)
│   │   ├── routes/
│   │   │   ├── auth.py          # Register, login, profile
│   │   │   ├── oauth.py         # Google OAuth2
│   │   │   ├── chat.py          # AI chat (OpenAI/Gemini)
│   │   │   ├── chatbots.py      # Chatbot CRUD
│   │   │   ├── api_keys.py      # API key management
│   │   │   ├── tts.py           # Text-to-Speech (Edge TTS)
│   │   │   ├── stt.py           # Speech-to-Text (Whisper)
│   │   │   ├── avatar.py        # Avatar viseme generation
│   │   │   ├── models.py        # Available LLM models
│   │   │   └── usage.py         # Usage analytics
│   │   ├── services/
│   │   │   ├── chat_service.py  # LLM integration
│   │   │   ├── tts_service.py   # Edge TTS wrapper
│   │   │   ├── stt_service.py   # Whisper STT wrapper
│   │   │   ├── avatar_service.py# Phoneme-to-viseme mapping
│   │   │   └── usage_service.py # Usage tracking
│   │   ├── middleware/
│   │   │   └── rate_limiter.py  # Sliding window rate limiting
│   │   └── websocket/
│   │       └── handlers.py      # WebSocket (chat, TTS, avatar)
│   └── requirements.txt
├── react-frontend/
│   └── src/
│       ├── App.js               # Main SPA (home + chat widget)
│       ├── contexts/
│       │   └── AuthContext.js    # Authentication state management
│       ├── pages/
│       │   ├── AuthPage.js      # Login/Register + Google OAuth
│       │   └── DashboardPage.js # Chatbots, API keys, usage
│       └── services/
│           └── api.js           # API client + WebSocket helpers
└── QUICKSTART.md
```

## Features

### Backend (FastAPI)
- **Auth**: JWT login/register + Google OAuth2
- **Chat**: OpenAI (GPT-3.5/4/4o) & Google Gemini, streaming via WebSocket
- **TTS**: Microsoft Edge TTS (cloud, free, 40+ voices)
- **STT**: OpenAI Whisper (local, base model ~140MB)
- **Avatar**: Phoneme-to-viseme mapping (MPEG-4 standard)
- **Chatbot Management**: CRUD with custom system prompts, model, voice, temperature
- **API Keys**: Generate/revoke keys with hashed storage
- **Usage Tracking**: Messages, tokens, audio seconds, cost analytics
- **Rate Limiting**: In-memory sliding window (60 req/min default)
- **Database**: SQLite via SQLAlchemy async (zero config)

### Frontend (React)
- **Landing Page**: Animated hero, feature cards, demo chat widget
- **Auth Pages**: Login/Register forms + Google OAuth button
- **Dashboard**: 4 tabs — Overview, Chatbots, API Keys, Usage
- **Chat Widget**: Real-time AI chat with WebSocket + REST fallback
- **Avatar**: Video avatar with lip-sync visemes
- **TTS/STT**: Voice input/output toggles in chat
- **Responsive**: Works on desktop and mobile

## API Endpoints (Key)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/oauth/google` | Google OAuth redirect |
| POST | `/api/chat` | Send chat message |
| WS | `/ws/chat` | WebSocket streaming chat |
| POST | `/api/tts` | Text-to-Speech |
| WS | `/ws/tts` | WebSocket TTS streaming |
| POST | `/api/stt` | Speech-to-Text |
| GET | `/api/chatbots` | List chatbots |
| POST | `/api/chatbots` | Create chatbot |
| GET | `/api/api-keys` | List API keys |
| POST | `/api/api-keys` | Generate API key |
| GET | `/api/usage/summary` | Usage analytics |
| GET | `/api/health` | Health check |

## Troubleshooting

### Backend won't start
```bash
cd backend
python --version  # Need 3.10+
python -m pip install -r requirements.txt
python -m uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload
```

### Frontend won't compile
```bash
cd react-frontend
rm -rf node_modules
npm install
npm start
```

### Chat returns mock responses
Set at least one LLM API key in `backend/.env`:
- `OPENAI_API_KEY` for GPT models
- `GEMINI_API_KEY` for Google Gemini

### Whisper model downloads slowly
First STT request downloads the base model (~140MB). Subsequent requests use the cached model.

### Google OAuth not working
1. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
2. Add `http://localhost:5000/api/auth/oauth/google/callback` as an authorized redirect URI in Google Cloud Console

## Performance Notes
- Whisper model (~140MB) is lazy-loaded on first STT request
- TTS uses cloud-based Microsoft Edge service (requires internet)
- SQLite database is created automatically at `backend/athena.db`
- Rate limiting defaults to 60 requests/minute per IP
- For production, consider PostgreSQL and Redis for persistence

---

**Last Updated**: March 5, 2026
