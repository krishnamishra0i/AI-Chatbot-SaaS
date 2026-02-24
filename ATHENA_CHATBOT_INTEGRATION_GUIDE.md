# Athena LMS AI Chatbot Integration Guide

## Overview
This is a modern, feature-rich chatbot UI for Athena LMS with Text-to-Speech (TTS), Speech-to-Text (STT), and integrated AI responses.

## Features

✅ **Avatar-Based UI** - Beautiful animated avatar with status indicators
✅ **Text-to-Speech (TTS)** - Automatic voice responses from the AI
✅ **Speech-to-Text (STT)** - Voice input with real-time transcription
✅ **Real-time Chat** - Instant message sending and receiving
✅ **Conversation History** - Maintains chat history during session
✅ **Responsive Design** - Works on desktop and mobile devices
✅ **Professional Theme** - Matches Athena LMS branding (burgundy/red theme)
✅ **Error Handling** - Graceful error messages and fallback options
✅ **Accessibility** - Keyboard shortcuts and screen reader support

## Files Included

1. **athena_chatbot_ui.html** - Standalone version with mock responses (no backend required)
2. **athena_chatbot_ui_advanced.html** - Full-featured version with backend API integration
3. **athena_chatbot_backend.py** - Flask backend server (handles AI integration)
4. **ATHENA_CHATBOT_INTEGRATION_GUIDE.md** - This guide

## Installation & Setup

### Option 1: Standalone Version (No Backend Required)

1. Open `athena_chatbot_ui.html` in any modern web browser
2. Click the floating 💬 button to open the chat
3. Use text or voice to chat with the mock AI

**Supported Browsers:**
- Chrome/Chromium (full support)
- Firefox (text only, no voice)
- Safari (full support)
- Edge (full support)

### Option 2: Full Integration with Backend

#### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Your existing AI integration (Groq or Google AI)

#### Step 1: Install Backend Dependencies

```bash
pip install flask flask-cors
```

If using Groq:
```bash
pip install groq
```

If using Google AI:
```bash
pip install google-generativeai
```

#### Step 2: Start the Backend Server

```bash
python athena_chatbot_backend.py
```

The server will start on `http://localhost:5000`

**Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

#### Step 3: Open the Advanced Frontend

Open `athena_chatbot_ui_advanced.html` in your browser

#### Step 4: Start Chatting!

- Type or speak (click 🎤) to send messages
- The AI will respond with both text and voice
- Chat history is maintained on the server

## Integration with Athena LMS Website

### Method 1: Embed in Existing Website

Add this code to your Athena LMS main page (before closing `</body>` tag):

```html
<!-- Athena AI Chatbot -->
<iframe 
    id="athena-chatbot"
    src="/athena_chatbot_ui_advanced.html"
    style="border: none; width: 100%; height: 100%; position: fixed; bottom: 0; right: 0; z-index: 9999;"
    allow="microphone">
</iframe>

<script>
    // Optional: Control chatbot from main page
    const chatbotFrame = document.getElementById('athena-chatbot');
    
    // Example: Open chatbot on button click
    document.getElementById('open-chat-btn')?.addEventListener('click', () => {
        chatbotFrame.contentWindow.openChat?.();
    });
</script>
```

### Method 2: Include as Script Tag

```html
<script src="/athena_chatbot_ui_advanced.html"></script>
```

### Method 3: React Component (if using React)

```jsx
import React from 'react';

export function AthenaAIChatbot() {
    return (
        <iframe
            src={process.env.PUBLIC_URL + '/athena_chatbot_ui_advanced.html'}
            style={{
                position: 'fixed',
                bottom: 0,
                right: 0,
                border: 'none',
                zIndex: 9999
            }}
            allow="microphone"
            title="Athena AI Assistant"
        />
    );
}
```

## Configuration

### Backend Configuration (athena_chatbot_backend.py)

```python
# API Configuration
API_URL = 'http://localhost:5000'
ENABLE_TTS = True
ENABLE_STT = True
LANGUAGE = 'en-US'

# AI Provider (automatic detection)
# The backend tries to use Groq first, then Google AI
# Configure your API keys in environment variables:
# GROQ_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
```

### Frontend Configuration (athena_chatbot_ui_advanced.html)

Edit the CONFIG object in the JavaScript section:

```javascript
const CONFIG = {
    apiUrl: 'http://localhost:5000',      // Backend URL
    enableTTS: true,                        // Enable text-to-speech
    enableSTT: true,                        // Enable speech-to-text
    language: 'en-US'                       // Language code
};
```

## API Endpoints

### POST /api/chat
Send a message and get response

**Request:**
```json
{
    "message": "What courses do you offer?"
}
```

**Response:**
```json
{
    "response": "We offer a wide variety of courses...",
    "timestamp": "2026-02-13T10:30:00"
}
```

### GET /api/chat/history
Get conversation history

**Response:**
```json
[
    {
        "role": "user",
        "content": "Hi",
        "timestamp": "2026-02-13T10:30:00"
    },
    {
        "role": "assistant",
        "content": "Hello! How can I help?",
        "timestamp": "2026-02-13T10:30:05"
    }
]
```

### POST /api/chat/clear
Clear conversation history

**Response:**
```json
{
    "status": "cleared"
}
```

### GET /api/health
Health check

**Response:**
```json
{
    "status": "healthy",
    "ai_available": true,
    "timestamp": "2026-02-13T10:30:00"
}
```

## Customization

### Change Avatar Emoji

In HTML, find:
```html
<div class="avatar" id="avatar">🤖</div>
```

Change 🤖 to any emoji you prefer, e.g.: 👩‍💼, 🦾, 🎓, etc.

### Change Colors

Edit the CSS gradients:
```css
/* Header background */
background: linear-gradient(135deg, #a62d2d 0%, #c41e3a 100%);

/* Button background */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change Voice

In JavaScript, customize the speech:
```javascript
utterance.rate = 1.0;      // 0.1 to 10 (slower to faster)
utterance.pitch = 1.0;     // 0 to 2 (lower to higher)
utterance.volume = 1.0;    // 0 to 1 (silent to loud)
```

## Troubleshooting

### Speech Recognition Not Working

**Issue:** "Speech recognition is not supported"

**Solution:**
- Use a supported browser (Chrome, Edge, Safari)
- HTTPS is required in production (not needed for localhost testing)
- Grant microphone permissions when prompted
- Check browser console for errors

### Backend Connection Error

**Issue:** "Make sure the backend is running on http://localhost:5000"

**Solution:**
```bash
# Check if backend is running
python athena_chatbot_backend.py

# Verify port is not in use
# Windows:
netstat -ano | findstr :5000

# Mac/Linux:
lsof -i :5000
```

### No Audio Output

**Issue:** TTS not working

**Solutions:**
- Check system volume
- Verify `enableTTS` is true in CONFIG
- Try a different voice rate/pitch
- Check browser audio permissions

### Missing AI Responses

**Issue:** Getting mock responses instead of AI responses

**Solution:**
- Check API keys are set: `GROQ_API_KEY` or `GOOGLE_API_KEY`
- Verify backend can access the AI API
- Check backend logs for errors
- May need to set `AI_AVAILABLE = False` in backend for testing

## Advanced Features

### Custom Response Handler

Modify `athena_chatbot_backend.py`:

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    # Your custom logic here
    message = request.json.get('message')
    
    # Get response from your custom system
    response = your_custom_ai_function(message)
    
    return jsonify({'response': response})
```

### Database Integration

Add conversation persistence:

```python
from sqlalchemy import create_engine, Column, String, DateTime
from datetime import datetime

# Create database table
class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(sa.Integer, primary_key=True)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

### Analytics Integration

Track user engagement:

```python
@app.route('/api/analytics/message', methods=['POST'])
def track_message():
    data = request.json
    # Log analytics
    return jsonify({'status': 'tracked'})
```

## Performance Tips

1. **Cache common responses** for faster replies
2. **Use CDN** for static assets in production
3. **Enable gzip compression** in Flask
4. **Use connection pooling** for database
5. **Implement rate limiting** to prevent abuse
6. **Load static files** from cache in browser

## Security Considerations

1. **CORS Configuration** - Update allowed origins:
```python
CORS(app, resources={r"/api/*": {"origins": ["yourdomain.com"]}})
```

2. **Input Sanitization** - The code escapes HTML, but validate on server
3. **HTTPS in Production** - Required for microphone access
4. **API Key Security** - Never expose API keys in frontend
5. **Rate Limiting** - Implement to prevent abuse

## Browser Support

| Browser | Text | Voice Input | Voice Output |
|---------|------|-------------|--------------|
| Chrome  | ✅   | ✅          | ✅           |
| Firefox | ✅   | ❌          | ✅           |
| Safari  | ✅   | ✅          | ✅           |
| Edge    | ✅   | ✅          | ✅           |
| IE 11   | ❌   | ❌          | ❌           |

## File Structure

```
Ai-Avater-Project/
├── athena_chatbot_ui.html                    # Standalone version
├── athena_chatbot_ui_advanced.html           # Full-featured version
├── athena_chatbot_backend.py                 # Flask backend
├── ATHENA_CHATBOT_INTEGRATION_GUIDE.md       # This guide
├── groq_chatbot_integration.py               # Your Groq integration
├── google_ai_integration_final.py            # Your Google AI integration
└── requirements.txt                          # Python dependencies
```

## Additional Resources

- **Web Speech API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **Flask Documentation:** https://flask.palletsprojects.com/
- **CORS in Flask:** https://flask-cors.readthedocs.io/
- **Groq API:** https://console.groq.com/docs/
- **Google Generative AI:** https://ai.google.dev/

## Support & Troubleshooting

For issues or questions:
1. Check the browser console (F12) for errors
2. Check backend terminal for error messages
3. Verify all files are in the correct location
4. Read the comments in the code for explanations
5. Test with the standalone version first

## Updates & Improvements

Planned enhancements:
- [ ] Avatar animations and gestures
- [ ] Multiple avatar options
- [ ] Chat history persistence (database)
- [ ] User authentication
- [ ] Multi-language support
- [ ] Sentiment analysis
- [ ] Real-time typing indicators
- [ ] File upload support
- [ ] Code syntax highlighting
- [ ] Dark/Light theme toggle

---

**Version:** 1.0
**Last Updated:** February 13, 2026
**Author:** Athena Development Team
