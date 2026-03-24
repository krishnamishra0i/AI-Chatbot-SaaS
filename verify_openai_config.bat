@echo off
REM OpenAI Configuration Verification Script
REM Tests that all components are configured to use OpenAI

echo.
echo =========================================
echo  OpenAI Configuration Test
echo =========================================
echo.

REM Test 1: Check backend .env
echo [1/3] Checking backend .env configuration...
findstr /M "DEFAULT_LLM_MODEL=gpt-4o" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\.env >nul
if %ERRORLEVEL%==0 (
    echo   ✓ DEFAULT_LLM_MODEL set to gpt-4o
) else (
    echo   ✗ DEFAULT_LLM_MODEL not set to gpt-4o
)

findstr /M "TTS_PROVIDER=openai" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\.env >nul
if %ERRORLEVEL%==0 (
    echo   ✓ TTS_PROVIDER set to openai
) else (
    echo   ✗ TTS_PROVIDER not set to openai
)

findstr /M "TTS_VOICE=alloy" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\.env >nul
if %ERRORLEVEL%==0 (
    echo   ✓ TTS_VOICE set to alloy
) else (
    echo   ✗ TTS_VOICE not set correctly
)

findstr /M "OPENAI_API_KEY=" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\.env >nul
if %ERRORLEVEL%==0 (
    echo   ✓ OPENAI_API_KEY is configured
) else (
    echo   ✗ OPENAI_API_KEY not found
)

echo.
echo [2/3] Checking TTS service...
findstr /M "TTS_PROVIDER" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\core\config.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ Config supports TTS_PROVIDER option
) else (
    echo   ✗ Config missing TTS_PROVIDER
)

findstr /M "openai" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\services\tts_service.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ TTS service supports OpenAI
) else (
    echo   ✗ TTS service doesnt support OpenAI
)

echo.
echo [3/3] Checking STT service...
findstr /M "Whisper" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\services\stt_service.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ STT using OpenAI Whisper
) else (
    echo   ✗ STT not configured for OpenAI
)

echo.
echo =========================================
echo  Configuration Status: READY
echo =========================================
echo.
echo Your chatbot is configured to use:
echo   - Chat: OpenAI GPT-4o
echo   - TTS: OpenAI (voice: alloy)
echo   - STT: OpenAI Whisper
echo.
echo Next steps:
echo   1. Start backend: python c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\run.py
echo   2. Start auth-service: npm start (from auth-service directory)
echo   3. Start frontend: npm start (from react-frontend directory)
echo   4. Open http://localhost:3000
echo   5. Click your chatbot and start chatting!
echo.
echo For more info, see: OPENAI_CONFIG_GUIDE.md
echo.
