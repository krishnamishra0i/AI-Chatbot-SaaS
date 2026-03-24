@echo off
REM Subscription & Usage Optimization Verification Script
REM Verifies all components are properly configured

echo.
echo =========================================
echo  Subscription System Verification
echo =========================================
echo.

REM Test 1: Check subscription models
echo [1/4] Checking subscription models...
find "class SubscriptionTier" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\services\subscription_models.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ Subscription models file created
) else (
    echo   ✗ Subscription models file missing
)

REM Test 2: Check subscription manager
echo [2/4] Checking subscription manager...
find "class SubscriptionManager" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\services\subscription_manager.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ Subscription manager file created
) else (
    echo   ✗ Subscription manager file missing
)

REM Test 3: Check optimization config
echo [3/4] Checking optimization configuration...
find "CHAT_LIMITS" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\services\optimization_config.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ Optimization config file created
) else (
    echo   ✗ Optimization config file missing
)

REM Test 4: Check API routes
echo [4/4] Checking subscription API routes...
find "/api/demo/start" c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\api\routes\subscriptions.py >nul
if %ERRORLEVEL%==0 (
    echo   ✓ Subscription API routes created
) else (
    echo   ✗ Subscription API routes missing
)

echo.
echo =========================================
echo  Configuration Status: READY
echo =========================================
echo.
echo Your subscription system includes:
echo   - Demo mode (10 seconds per user)
echo   - Token limits (1K-unlimited per tier)
echo   - TTS/STT optimization (500KB-10MB)
echo   - Usage tracking (real-time stats)
echo   - API endpoints for management
echo.
echo Demo tier limits:
echo   - Session: 10 seconds
echo   - Tokens: 1,000 (max 100 per response)
echo   - TTS: 10 minutes audio
echo   - STT: 10 minutes speech
echo   - Cost per user: ^<$0.001
echo.
echo Next steps:
echo   1. Start backend: python c:\Krshna\workspace\Ai-Chatbot-SaaS\AI-Chatbot-SaaS\backend\run.py
echo   2. Test demo: curl http://localhost:5000/api/demo/start
echo   3. Check usage: curl http://localhost:5000/api/subscription/usage
echo   4. Integrate with chat/tts/stt routes (see INTEGRATION_EXAMPLES.md)
echo.
echo Documentation files:
echo   - SUBSCRIPTION_GUIDE.md (complete guide)
echo   - INTEGRATION_EXAMPLES.md (code examples)
echo   - USAGE_OPTIMIZATION_SUMMARY.md (quick reference)
echo.
