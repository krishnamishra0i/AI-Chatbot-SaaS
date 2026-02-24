# 🤖 AI Avatar Chatbot

A professional, full-featured AI chatbot with animated avatars, real-time voice I/O, and advanced RAG (Retrieval-Augmented Generation) capabilities.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking: MyPy](https://img.shields.io/badge/type%20check-mypy-blue.svg)](https://mypy-lang.org/)

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Modal Chat**: Text, voice, and animated avatar interactions
- **Advanced RAG**: Semantic search through 126+ documents (knowledge base + support tickets)
- **Multiple LLM Providers**: Groq, OpenAI, Anthropic, and local models
- **Real-Time TTS/STT**: Natural voice synthesis and recognition
- **Vector Database**: ChromaDB with BAAI/bge-base-en-v1.5 embeddings
- **Modern UI**: React 18 + TypeScript frontend

### 🚀 Production Ready
- **Async Architecture**: Full async/await implementation
- **Scalable Design**: Modular, microservice-ready architecture
- **Comprehensive Testing**: 80%+ test coverage
- **Monitoring**: Built-in metrics and health checks
- **Security**: JWT authentication and input validation
- **Docker Support**: Containerized deployment

## 📁 Project Structure

```
ai-avatar-chatbot/
├── 📁 .github/                 # GitHub Actions, issue templates
├── 📁 docs/                    # Documentation, API docs
├── 📁 scripts/                 # Setup and utility scripts
├── 📁 src/                     # Source code
│   ├── 📁 backend/            # FastAPI backend
│   │   ├── 📁 api/            # API routes and endpoints
│   │   ├── 📁 asr/            # Speech-to-text (Whisper)
│   │   ├── 📁 config/         # Configuration management
│   │   ├── 📁 llm/            # LLM integrations
│   │   ├── 📁 rag/            # RAG system (vector DB + retrieval)
│   │   ├── 📁 tts/            # Text-to-speech engines
│   │   ├── 📁 utils/          # Utilities and helpers
│   │   └── main_enhanced.py   # Application entry point
│   ├── 📁 frontend/           # React frontend
│   │   ├── 📁 src/
│   │   ├── 📁 public/
│   │   └── package.json
│   ├── 📁 data/               # Knowledge base and vector DB
│   └── 📁 shared/             # Shared types and utilities
├── 📁 tests/                   # Comprehensive test suite
├── 📁 tools/                   # Development and deployment tools
├── 📁 docker/                  # Docker configurations
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Git**

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-avatar-chatbot.git
cd ai-avatar-chatbot

# Run the automated setup script
python scripts/setup_dev.py
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required API keys:
```env
# LLM Providers (choose at least one)
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: Avatar services
D_ID_API_KEY=your_d_id_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### 3. Start the Application
```bash
# Start backend (terminal 1)
python -m src.backend.main_enhanced

# Start frontend (terminal 2)
cd src/frontend && npm run dev

# Visit http://localhost:8000
```

## 📚 API Documentation

### REST Endpoints

#### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, how can I help you?",
  "mode": "text|voice",
  "session_id": "optional_session_id"
}
```

#### Voice
```http
POST /api/tts
Content-Type: multipart/form-data

# Text-to-Speech
text=Hello%20World&voice=en-US-Aria

POST /api/stt
Content-Type: multipart/form-data

# Speech-to-Text (upload audio file)
audio_file=@recording.wav
```

#### Knowledge Base
```http
GET /api/search?q=credit%20score&limit=5
POST /api/ingest
Content-Type: application/json

{
  "documents": [
    {
      "content": "Your document text here",
      "metadata": {"source": "manual"}
    }
  ]
}
```

### WebSocket
```javascript
// Real-time chat
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data.message);
};
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_backend.py -v    # Backend tests
pytest tests/test_rag.py -v       # RAG system tests
pytest tests/test_api.py -v       # API endpoint tests

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full user journey testing
- **Performance Tests**: Load and stress testing

## 🛠 Development

### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

### Adding New Features

#### 1. LLM Provider
```python
# src/backend/llm/your_provider.py
from backend.llm.base import LLMProvider

class YourProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        # Your implementation
        pass
```

#### 2. TTS Engine
```python
# src/backend/tts/your_tts.py
from backend.tts.base import TTSEngine

class YourTTS(TTSEngine):
    async def synthesize(self, text: str) -> bytes:
        # Your implementation
        pass
```

#### 3. API Endpoint
```python
# src/backend/api/your_endpoint.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/your-endpoint")
async def your_function():
    return {"message": "Hello from your endpoint!"}
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t ai-avatar-chatbot .
docker run -p 8000:8000 ai-avatar-chatbot
```

### Cloud Deployment
- **AWS**: ECS Fargate with ALB
- **GCP**: Cloud Run with Cloud Build
- **Azure**: Container Apps with API Management

### Production Checklist
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Rate limiting configured
- [ ] Security headers enabled

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db

# External services
curl http://localhost:8000/health/external
```

### Metrics
- **Response Times**: P95 < 2 seconds
- **Error Rate**: < 1%
- **Uptime**: 99.9%
- **Throughput**: 100+ requests/minute

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** changes: `git commit -m 'Add your feature'`
4. **Push** to branch: `git push origin feature/your-feature`
5. **Create** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add type hints for all functions
- Write comprehensive tests
- Update documentation
- Use conventional commits

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern async web framework
- **React**: Frontend library
- **ChromaDB**: Vector database
- **BAAI/bge-base-en-v1.5**: High-quality embeddings
- **Whisper**: Speech recognition
- **Edge TTS**: Neural voice synthesis

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-avatar-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-avatar-chatbot/discussions)
- **Documentation**: [Read the Docs](https://ai-avatar-chatbot.readthedocs.io/)

---

**Made with ❤️ for the AI community**
| **LLM** | Groq | Fast inference (llama-3.1-8b, 70b options) |
| **Voice Input** | Whisper | Accurate speech-to-text |
| **Voice Output** | Edge TTS | Natural neural voices |
| **Avatar Video** | D-ID API | Professional animated avatars |
| **Knowledge Base** | RAG + Vector DB | Semantic search, context-aware |
| **Backend** | FastAPI | Async, streaming, production-ready |
| **Frontend** | React 18 + TS | Modern, responsive, polished UI |

---

## 📦 What's Included

```
ai_avatar_chatbot/
├── 🔧 backend/
│   ├── main.py                           # FastAPI app
│   ├── api/
│   │   ├── chat_routes.py               # Chat endpoint
│   │   ├── tts_stt_routes.py            # Voice endpoints
│   │   └── d_id_routes.py               # Avatar endpoints (NEW)
│   ├── avatar/
│   │   ├── d_id_integration.py          # D-ID setup
│   │   └── d_id_api.py                  # D-ID async client (NEW)
│   ├── llm/
│   │   ├── groq_llm.py                  # Groq integration
│   │   └── prompt.py                    # System prompts
│   ├── tts/
│   │   └── modern_tts.py               # Edge TTS
│   ├── asr/
│   │   └── whisper_stt.py              # Whisper STT
│   └── rag/
│       └── retriever.py                # Knowledge base
│
├── 🎨 frontend/
│   ├── src/
│   │   ├── App.tsx                      # Mode selector (NEW)
│   │   ├── components/
│   │   │   ├── FloatingAvatarChatbot.tsx    # Split-screen mode
│   │   │   └── RealTimeAvatar.tsx          # D-ID mode (NEW)
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
│
├── 📚 data/
│   ├── knowledge_base/                  # Your documents here
│   └── vector_db/                       # Embeddings stored
│
├── 🔐 .env                              # Your API keys
├── requirements.txt                    # Python dependencies
└── SETUP_GUIDE.md                      # Detailed setup
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Get API Keys (FREE)
- **Groq**: https://console.groq.com (free tier unlimited)
- **D-ID**: https://www.d-id.com (free trial with credits)

### 2. Configure
```bash
cd ai_avatar_chatbot
cp .env.example .env
# Edit .env with your API keys
```

### 3. Install & Run
```bash
# Terminal 1: Backend
pip install -r requirements.txt
uvicorn backend.main:app --port 8001 --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### 4. Open Browser
```
🌐 http://localhost:3000
```

**See more details in [QUICK_START.md](QUICK_START.md)**

---

## 🎮 Usage

### Split-Screen Chat (No Setup)
1. Click "Split-Screen Chat" on home
2. Type or record voice message
3. AI responds instantly
4. Avatar text appears on screen

### D-ID Real-Time Avatar (Needs D-ID Key)
1. Click "D-ID Real-time Avatar" on home
2. Paste your D-ID API key
3. Send message or record voice
4. Watch animated avatar respond with video
5. Avatar speaks your response

### Voice Input
- Click the 🎤 microphone button
- Speak your message
- Click again to stop
- Message auto-transcribes

### Text Input
- Type in message box
- Press Enter or click Send
- Get instant AI response
- Avatar video generates (D-ID mode)

---

## 🏗️ Architecture

### Backend Flow
```
User Input (text/voice)
    ↓
[FastAPI Router]
    ↓
    ├→ Text preprocessing
    ├→ Knowledge base search (if enabled)
    ├→ Groq LLM processing
    ├→ TTS generation (Edge TTS)
    └→ D-ID video generation (if enabled)
    ↓
Streaming Response
    ↓
Frontend (Real-time updates)
```

### Frontend Flow
```
User Action
    ↓
[React Component]
    ↓
    ├→ Text input / Voice recording (Whisper)
    ├→ Send to backend
    └→ Stream response
    ↓
    ├→ Update chat panel
    ├→ Play audio (TTS)
    └→ Display video (D-ID)
    ↓
Render to Screen
```

---

## 🔌 API Endpoints

### Chat API
```bash
# Send message, get text response
POST /api/chat
{
  "message": "What is quantum computing?",
  "use_knowledge_base": true
}

# Get streaming response
POST /api/avatar/chat-with-avatar
{
  "message": "Hello!",
  "avatar_image_url": "https://..."
}
```

### Voice API
```bash
# Convert audio to text
POST /api/stt/transcribe
(audio file)

# Convert text to audio
POST /api/tts/synthesize-audio
{
  "text": "Hello, how are you?",
  "voice": "en-US-AvaNeural"
}
```

### Avatar API
```bash
# Generate talking video
POST /api/avatar/generate-video
{
  "message": "Hello world",
  "avatar_image_url": "https://..."
}

# Check video status
GET /api/avatar/video-status/{talk_id}

# Full chat with avatar
POST /api/avatar/chat-with-avatar
{
  "message": "Hello!",
  "avatar_image_url": "https://..."
}
```

### Health Check
```bash
GET /health
```

**Full API docs**: `http://localhost:8001/docs`

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
# 🔑 API Keys
GROQ_API_KEY=gsk_...
D_ID_API_KEY=xxx...
WHISPER_API_KEY=sk-...  # Optional, uses local Whisper

# 🎙️ Voice Settings
EDGE_TTS_VOICE=en-US-AvaNeural
EDGE_TTS_RATE=1.0

# 🤖 LLM Settings
LLM_MODEL_NAME=llama-3.1-8b-instant  # Fast
# OR: llama-3.1-70b-versatile        # Better quality
# OR: gemma-7b-it                    # Balanced

# 🌐 Server Settings
API_HOST=127.0.0.1
API_PORT=8001
DEBUG=false

# 📚 Knowledge Base
RAG_SIMILARITY_THRESHOLD=0.5
RAG_TOP_K=3

# 🎬 D-ID Avatar
D_ID_API_URL=https://api.d-id.com
D_ID_PRESENTER_ID=default
```

### LLM Model Options
| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `gemma-7b-it` | ⚡⚡⚡ | ⭐⭐ | Fast responses |
| `llama-3.1-8b-instant` | ⚡⚡ | ⭐⭐⭐ | Balanced (DEFAULT) |
| `llama-3.1-70b-versatile` | ⚡ | ⭐⭐⭐⭐⭐ | Best quality |

### Voice Options
```
en-US-AvaNeural (Female, default)
en-US-AriaNeural (Female)
en-US-GuyNeural (Male)
en-GB-SophieNeural (British Female)
en-AU-NatashaNeural (Australian Female)
// ... 100+ more voices available
```

---

## 📚 Knowledge Base Setup

### Add Documents
1. Place PDF/TXT files in `data/knowledge_base/`
2. Run import:
   ```bash
   python -c "from backend.rag.ingest import load_documents; load_documents()"
   ```
3. Embeddings are created and stored in `data/vector_db/`
4. When chatting, enable `use_knowledge_base: true`

### Example Usage
```python
# Backend sees this:
{
  "message": "What is company policy on remotes?",
  "use_knowledge_base": true
}

# Automatically searches through your documents
# Includes relevant context in LLM prompt
# Returns answer from your knowledge
```

---

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8001/health
```

### Test Chat API
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello AI!"}' 
```

### Test Voice APIs
```bash
# Test TTS
curl -X POST http://localhost:8001/api/tts/synthesize-audio \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'

# Test STT (with audio file)
curl -X POST http://localhost:8001/api/stt/transcribe \
  -F "file=@audio.wav"
```

### Test D-ID Avatar
```bash
curl -X POST http://localhost:8001/api/avatar/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello world",
    "avatar_image_url": "https://example.com/avatar.png"
  }'
```

---

## 🛠️ Customization

### Change Avatar Image
Edit `frontend/src/components/RealTimeAvatar.tsx`:
```tsx
const avatarImageUrl = "YOUR_CUSTOM_IMAGE_URL";
```

### Change System Prompt
Edit `backend/llm/prompt.py`:
```python
SYSTEM_PROMPT = """You are a helpful AI assistant...
Your custom instructions here...
"""
```

### Change UI Theme
Edit `frontend/src/index.css`

### Change Backend Port
Edit `.env`:
```env
API_PORT=8002  # Use different port
```

---

## 📊 Features Comparison

| Feature | Split-Screen | D-ID Avatar |
|---------|-------------|------------|
| No setup | ✅ | ❌ Need D-ID key |
| Text chat | ✅ | ✅ |
| Voice input | ✅ | ✅ |
| Avatar video | ❌ Static | ✅ Animated |
| Real-time | ✅ | ✅ Streaming |
| Cost | Free | D-ID credits |
| Professional | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔐 Security & API Keys

### Keep Your Keys Safe ✅
```bash
# ✅ GOOD
GROQ_API_KEY=sk_xxx  # In .env (locally)

# ❌ NEVER
git commit .env
GROQ_API_KEY=sk_xxx  # In code
// hardcoded keys
```

### Get API Keys Safely
- **Groq**: https://console.groq.com/keys
- **D-ID**: https://www.d-id.com/api
- Store in `.env` (not in git)
- Use environment variables in production

### Free Tier Limits
- **Groq**: Unlimited API calls (generous free tier)
- **D-ID**: ~1000 minutes video/month free trial
- **Whisper TTS**: Free with Edge TTS (no credits needed)

---

## 🚀 Production Deployment

### Prepare for Production
1. Set `DEBUG=false` in `.env`
2. Use production LLM model (70b for quality)
3. Set up monitoring/logging
4. Configure CORS for your domain
5. Use environment variables (never hardcode keys)
6. Set up knowledge base with your documents

### Deploy Backend
```bash
# Using Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  backend.main:app

# Using Docker
docker build -t avatar-chatbot .
docker run -p 8001:8001 avatar-chatbot
```

### Deploy Frontend
```bash
# Build optimized version
npm run build

# Deploy to Vercel, Netlify, etc
# Or serve from your server
vercel deploy
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**Backend won't start**
```bash
# Check Python version (3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port is free
lsof -i :8001  # (or netstat on Windows)
```

**API key not working**
```bash
# Verify key format (no spaces/quotes)
echo $GROQ_API_KEY  # Check it loaded

# Test API key
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.groq.com/...
```

**Avatar video not generating**
- D-ID account needs to be activated
- Check API key has valid quota
- Try with public image URL first
- Monitor their API status page

**Voice input not working**
- Check microphone permissions in browser
- Verify browser supports Web Audio API
- Try different browser if stuck
- Check console for errors (F12)

**Slow LLM responses**
- Use faster model: `gemma-7b-it`
- Check Groq quota/rate limits
- Monitor network latency
- Try local LLM as fallback

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed troubleshooting**

---

## 📖 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed configuration
- **API Docs** - `http://localhost:8001/docs` (after running backend)
- **Groq API** - https://console.groq.com/docs
- **D-ID API** - https://docs.d-id.com
- **Whisper** - https://openai.com/research/whisper

---

## 🤝 Contributing

Have ideas to improve the chatbot?
1. Fork the repository
2. Create feature branch
3. Test your changes
4. Submit pull request

---

## 📄 License

MIT License - Feel free to use in personal and commercial projects

---

## 🎓 Learning Resources

### Understanding the Stack
- **FastAPI**: Modern Python web framework
- **React 18**: Frontend UI library with hooks
- **Groq**: Fast inference API
- **D-ID**: Avatar video generation
- **RAG**: Retrieval-Augmented Generation for knowledge

### Getting Started References
1. Start with [QUICK_START.md](QUICK_START.md)
2. Run both backend and frontend
3. Test split-screen chat first
4. Then try D-ID mode with API key
5. Customize with your own avatar/knowledge

---

## ❓ FAQ

**Q: Do I need D-ID to use the chatbot?**
A: No! Split-screen mode works without D-ID. D-ID adds animated videos (optional).

**Q: What's the cost?**
A: Groq is free unlimited. D-ID has free trial with credits (~1000 min/month).

**Q: Can I use my own avatar?**
A: Yes! Upload to D-ID and use the image URL in RealTimeAvatar.tsx

**Q: How do I add custom knowledge?**
A: Put documents in `data/knowledge_base/` and enable RAG in chat.

**Q: Can I deploy this?**
A: Yes! See Production Deployment section above.

**Q: Which LLM model is best?**
A: llama-3.1-8b-instant (default) balances speed/quality. Use 70b for premium responses.

**Q: How many users can it handle?**
A: Depends on deployment. Single instance: ~50-100 concurrent. Scale with load balancing.

---

## 🌟 Show Your Support

If you found this useful:
- ⭐ Star the repository
- 🐛 Report issues
- 💡 Suggest features
- 📢 Share with others

---

## 📞 Support

- **Issues**: GitHub Issues
- **Docs**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API Help**: Check `/docs` endpoint
- **Questions**: Check FAQ above

---

**Built with ❤️ for AI enthusiasts**

Start chatting with your D-ID avatar today! 🎬
