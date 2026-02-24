# Google AI Integration Setup Guide

## Overview
This guide helps you set up real-time intelligent responses for your ATHENA chatbot using Google's Generative AI (Gemini) API.

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A Google account

## Step 1: Get Your Google API Key

### Option A: Using Google AI Studio (Recommended)
1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/app/apikey

2. **Create/Get API Key:**
   - Click "Create API Key" or "Get API key"
   - Select your Google project (or create a new one)
   - Copy your API key to a safe place

3. **Note:** Google AI Studio provides free access to Gemini models with usage limits.

### Option B: Using Google Cloud Console
1. **Create a Google Cloud Project:**
   - Go to: https://console.cloud.google.com/
   - Click "Create Project"
   - Enter project name and click "Create"

2. **Enable Generative AI API:**
   - In the Cloud Console, search for "Generative Language API"
   - Click on it and select "Enable"

3. **Create API Key:**
   - Go to "Credentials" in left menu
   - Click "Create Credentials" → "API Key"
   - Copy your API key

## Step 2: Install Required Package

```bash
pip install google-generativeai
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:
```
google-generativeai>=0.3.0
flask>=2.0.0
flask-cors>=3.0.10
```

## Step 3: Configure Your API Key

### Option A: Environment Variable (Recommended)
**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**Mac/Linux:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Then run your backend:
```bash
python athena_chatbot_backend.py
```

### Option B: Direct in Code
Edit `google_ai_chatbot.py` and modify:
```python
self.api_key = "your-api-key-here"  # Replace with your actual key
```

### Option C: .env File
1. Create a `.env` file in your project root:
```
GOOGLE_API_KEY=your-api-key-here
```

2. Install python-dotenv:
```bash
pip install python-dotenv
```

3. The chatbot will automatically load it.

## Step 4: Verify Installation

Run the test:
```bash
python google_ai_chatbot.py
```

You should see:
```
=== Testing Google AI Chatbot ===

User: What is ATHENA AI?
Bot: [Google AI response here]

✓ Test completed successfully!
```

## Step 5: Start Your Application

1. **Start the Flask backend:**
```bash
python athena_chatbot_backend.py
```

2. **Open the chatbot:**
Visit: `http://localhost:8000/athena_enterprise_platform.html`

3. **Test in your browser:**
- Click the 💬 chatbot button
- Type a message
- You should get real-time AI responses!

## Troubleshooting

### Error: "Google API key not found"
- ✓ Check you've set the GOOGLE_API_KEY environment variable
- ✓ Verify the key is correct (should be ~39 characters)
- ✓ Restart your terminal/application after setting the environment variable

### Error: "Invalid API key"
- ✓ Copy your key again from Google AI Studio or Cloud Console
- ✓ Make sure there are no extra spaces
- ✓ Check the key hasn't expired

### Error: "API key has project restrictions"
- ✓ Go to Google Cloud Console
- ✓ Select your project
- ✓ Go to Credentials → Your API Key
- ✓ Edit "API restrictions" → Select "Generative Language API"
- ✓ Remove any project restrictions

### Slow responses
- This is normal for the first response (cold start)
- Responses should be < 3 seconds after that
- Upgrade your API tier if needed for higher rate limits

### No AI responses (using mock responses)
- Check backend console for error messages
- Verify GOOGLE_API_KEY environment variable is set
- Test with: `python google_ai_chatbot.py`
- Check internet connection

## Model Information

- **Model:** `gemini-1.5-flash` (fast, cost-effective)
- **Alternative:** `gemini-1.5-pro` (more capable, slower)
- **Cost:** Free tier provides adequate usage for most applications
- **Features:**
  - Real-time responses
  - Context-aware answers
  - Multi-turn conversations
  - ~3-5 second response time

## API Usage Limits (Free Tier)

- **Requests:** 60 per minute
- **Tokens:** 1 million per month
- **Response:** Up to 8,000 tokens
- For higher limits, upgrade to paid tier

## Features Your Chatbot Now Has

✅ Real-time intelligent responses  
✅ Context-aware conversations  
✅ Knowledge about ATHENA AI  
✅ Personalized learning recommendations  
✅ 24/7 availability  
✅ Multi-language support (by default)  
✅ Conversation history (last 10 exchanges)  

## Security Notes

⚠️ **Important:**
- Never commit your API key to version control
- Use environment variables only
- Consider using Google Cloud's key management for production
- Monitor your API usage in Google Cloud Console
- Rotate your API key periodically

## Next Steps

1. ✅ Get your API key
2. ✅ Install google-generativeai
3. ✅ Set GOOGLE_API_KEY environment variable
4. ✅ Run the chatbot
5. ✅ Test in your browser
6. ✅ Customize the system prompt if needed

## Support

For issues:
1. Check the logs: Look at console output when backend runs
2. Test directly: Run `python google_ai_chatbot.py`
3. Verify API key: Go to Google AI Studio and confirm key works
4. Check network: Ensure internet connection for API calls

## File Structure

```
your-project/
├── athena_chatbot_backend.py      # Flask backend (updated)
├── google_ai_chatbot.py            # Google AI integration (new)
├── athena_enterprise_platform.html # Frontend with chatbot
├── requirements.txt                # Python dependencies
└── .env                           # Your API key (optional)
```

---

**Ready to go!** 🚀 Your ATHENA chatbot now has real-time intelligent responses powered by Google's Gemini AI!
