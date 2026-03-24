"""
Complete Auth Flow Test - Chatbot Authentication
Tests: Register → Login → Get Profile → Create Chatbot
Updated for backend/tests/auth location
"""
import requests
import json

BASE_URL = "http://localhost:5000"
AUTH_SERVICE = "http://localhost:3001"

print("=" * 80)
print("🔐 COMPLETE CHATBOT AUTH FLOW TEST")
print("=" * 80)

# ── Test 1: Register User ──────────────────────────────────────────────────

print("\n[TEST 1] Register new user via backend")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": "chatbot-test@example.com",
            "password": "SecurePass123!",
            "name": "Chatbot Tester"
        },
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        access_token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        print(f"  ✅ Registered successfully")
        print(f"  User ID: {user_id}")
        print(f"  Token: {access_token[:40]}...")
    else:
        print(f"  ❌ Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    exit(1)

# ── Test 2: Verify Token ───────────────────────────────────────────────────

print("\n[TEST 2] Verify token with GET /api/auth/me")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers,
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        me_data = response.json()
        print(f"  ✅ Token verified")
        print(f"  Email: {me_data.get('email')}")
    else:
        print(f"  ❌ Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    exit(1)

# ── Test 3: Create Chatbot ─────────────────────────────────────────────────

print("\n[TEST 3] Create a chatbot")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{BASE_URL}/api/chatbots",
        json={
            "name": "Test Bot",
            "description": "Testing auth flow",
            "model": "gpt-4o-mini"
        },
        headers=headers,
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 201:
        chatbot = response.json()
        bot_id = chatbot.get("id")
        print(f"  ✅ Chatbot created")
        print(f"  Bot ID: {bot_id}")
    else:
        print(f"  ❌ Failed: {response.text}")
        print(f"  Response headers: {response.headers}")
        exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    exit(1)

# ── Test 4: List Chatbots ─────────────────────────────────────────────────

print("\n[TEST 4] List all chatbots (verify creation)")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{BASE_URL}/api/chatbots",
        headers=headers,
        timeout=5
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        chatbots = data.get("data", data) if isinstance(data, dict) else data
        print(f"  ✅ Found {len(chatbots)} chatbot(s)")
        for bot in chatbots:
            print(f"     - {bot.get('name', bot.get('id'))}")
    else:
        print(f"  ❌ Failed: {response.text}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ── Test 5: Send Chat Message ──────────────────────────────────────────────

print("\n[TEST 5] Send chat message to chatbot")
try:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Hello, bot!",
            "session_id": bot_id,
            "model": "gpt-4o-mini"
        },
        headers=headers,
        timeout=10
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print(f"  ✅ Chat message sent successfully")
    else:
        print(f"  ⚠️  Status {response.status_code}: {response.text[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ COMPLETE AUTH FLOW TEST FINISHED")
print("=" * 80)
