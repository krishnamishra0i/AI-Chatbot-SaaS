# AI Avatar Chatbot with Real-time Voice & Text

A complete AI chatbot application with voice input/output, text generation, and optional avatar/lip-sync capabilities. Built with FastAPI, Whisper (Speech-to-Text), XTTS (Text-to-Speech), and LLM integration with RAG support.

## Features

- 🎙️ **Speech-to-Text (ASR)**: Real-time speech recognition using OpenAI Whisper
- 🔊 **Text-to-Speech (TTS)**: Natural voice synthesis using XTTS v2
- 🤖 **LLM Integration**: Support for Ollama, OpenAI, and other LLM providers
- 📚 **RAG (Retrieval-Augmented Generation)**: Knowledge base integration for enhanced responses
- 🌐 **WebSocket Support**: Real-time bidirectional communication
- 💬 **Modern UI**: Beautiful chat interface with avatar display
- 🎭 **Optional Avatar**: Lip-sync with Wav2Lip (optional)
- 🌍 **Multi-language**: Support for multiple languages
- 🔧 **Easy Configuration**: Simple settings management

## Project Structure

```
ai_avatar_chatbot/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Settings and configuration
│   ├── api/
│   │   ├── websocket.py        # WebSocket handling
│   │   ├── chat_routes.py      # REST API routes
│   │   └── health.py           # Health check
│   ├── asr/                    # Speech-to-Text
│   │   ├── whisper_stt.py      # Whisper integration
│   │   └── vad.py              # Voice Activity Detection
│   ├── tts/                    # Text-to-Speech
│   │   ├── xtts_tts.py         # XTTS integration
│   │   └── audio_utils.py      # Audio utilities
│   ├── llm/                    # Language Model
│   │   ├── llm.py              # LLM interface
│   │   └── prompt.py           # Prompt templates
│   ├── rag/                    # Retrieval-Augmented Generation
│   │   ├── ingest.py           # Document ingestion
│   │   ├── retriever.py        # Document retrieval
│   │   └── vectordb.py         # Vector database
│   └── utils/
│       ├── audio_buffer.py     # Audio buffering
│       └── logger.py           # Logging setup
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css               # Styling
│   ├── app.js                  # Frontend logic
│   └── avatar/                 # Avatar components
├── models/                     # Pre-trained models
├── training/                   # Training scripts
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.9+
- FFmpeg (for audio processing)
- GPU support (optional, for faster inference)

### Step 1: Clone and Setup

```bash
cd ai_avatar_chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Download Models (Optional)

The first run will automatically download models. For faster startup, you can pre-download:

```bash
# Download Whisper model
python -c "import whisper; whisper.load_model('base')"

# Download TTS model
python -m TTS.cli --text "Hello" --model_name "tts_models/en/ljspeech/xtts_v2"
```

## Quick Start

### 1. Start Local LLM (Optional but Recommended)

Using Ollama (recommended):

```bash
# Download and install from https://ollama.ai
ollama serve
# In another terminal:
ollama pull mistral
```

Or use OpenAI API:
```bash
export OPENAI_API_KEY="your-api-key"
```

### 2. Start Backend Server

```bash
cd backend
python main.py
```

Server starts at `http://localhost:8000`

### 3. Access Frontend

Open browser and navigate to:
```
http://localhost:8000/static/index.html
```

Or serve frontend separately:
```bash
cd frontend
python -m http.server 8080
# Visit http://localhost:8080
```

## Usage

### Text Chat
1. Type your message in the input box
2. Click Send or press Enter
3. Get AI response with text-to-speech

### Voice Chat
1. Click the microphone button
2. Speak your question
3. Stop recording (red button)
4. Get transcribed text and AI response

### Settings
1. Click the settings icon
2. Adjust language, voice speed, and server URL
3. Settings are saved locally

## API Endpoints

### REST API

```
POST /api/chat
{
  "message": "Hello",
  "language": "en"
}

Response:
{
  "response": "Hello! How can I help?",
  "language": "en"
}
```

### WebSocket

```
ws://localhost:8000/ws/chat

Send: {"type": "text", "message": "Hello"}
Receive: {"type": "text", "message": "Response"}

Send audio: {"type": "audio", "audio_data": [...]}
Receive: {"type": "transcription", "text": "..."}
```

## Configuration

Edit `backend/config.py` to customize:

```python
# ASR
ASR_MODEL_NAME = "openai/whisper-small"  # tiny, base, small, medium, large
ASR_DEVICE = "cuda"  # or "cpu"

# TTS
TTS_MODEL_NAME = "tts_models/en/ljspeech/xtts_v2"
TTS_DEVICE = "cuda"

# LLM
LLM_MODEL_NAME = "mistral-7b"
LLM_API_URL = "http://localhost:11434"  # Ollama

# Audio
SAMPLE_RATE = 16000
MAX_AUDIO_LENGTH = 60
```

## Advanced Features

### RAG Integration

Add knowledge base documents:

```python
from backend.rag import DocumentIngestor, SimpleVectorDB, Retriever

# Create vector database
vector_db = SimpleVectorDB()
ingestor = DocumentIngestor(vector_db)

# Ingest documents
ingestor.ingest_file("document.txt")
ingestor.ingest_directory("knowledge_base/")

# Use for retrieval
retriever = Retriever(vector_db)
context = retriever.get_context("user question")
```

### Custom LLM Providers

```python
from backend.llm import LLMInterface

# Ollama (default)
llm = LLMInterface(provider="ollama", model="mistral")

# OpenAI
llm = LLMInterface(provider="openai", model="gpt-3.5-turbo")
```

### Voice Cloning (TTS)

```python
from backend.tts import XTTSVTS

tts = XTTSVTS()
audio = tts.synthesize(
    text="Hello world",
    speaker_wav="path/to/reference_voice.wav"  # Voice cloning
)
```

## Troubleshooting

### Microphone Issues
- Check browser permissions for microphone access
- In Chrome: Settings → Privacy → Microphone

### Audio Quality
- Adjust `SAMPLE_RATE` and `CHUNK_SIZE` in config
- Use "cuda" device if GPU available

### Slow Responses
- Use smaller models: whisper-tiny, whisper-base
- Enable GPU (CUDA) support
- Use quantized models

### WebSocket Connection Issues
- Ensure backend is running
- Check CORS settings
- Verify WebSocket URL in frontend settings

## Performance Tips

1. **GPU Support**: Install CUDA for ~10x faster inference
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Model Size**: Use smaller models for faster response
   - ASR: whisper-tiny → base → small
   - TTS: Use pre-downloaded models

3. **Caching**: Enable local caching for embeddings

## Development

### Adding New Modules

1. Create module in `backend/`
2. Add initialization in `backend/main.py`
3. Add API routes if needed
4. Update requirements.txt

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Chat API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

## License

MIT License - feel free to use for personal and commercial projects

## Support

For issues and questions:
1. Check troubleshooting section
2. Review logs in console output
3. Open an issue on GitHub

## Future Enhancements

- [ ] Avatar/Lip-sync with Wav2Lip
- [ ] Real-time emotion detection
- [ ] Multi-user support
- [ ] Database persistence
- [ ] Advanced RAG with semantic search
- [ ] Model fine-tuning UI
- [ ] Video input support
- [ ] Integration with more LLMs

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request

---

**Happy chatting with your AI Avatar! 🎉**
