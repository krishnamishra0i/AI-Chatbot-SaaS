"""
Auth Flow Test with Extended Timeout
Updated for backend/tests/auth location
"""
import requests
import time

print("Testing backend connectivity with extended timeout...")

for attempt in range(1, 4):
    try:
        print(f"\n[Attempt {attempt}] Testing /api/health with 10s timeout...")
        resp = requests.get("http://localhost:5000/api/health", timeout=10)
        print(f"✅ Health check: {resp.status_code}")
        
        print(f"[Attempt {attempt}] Testing /api/auth/register with 15s timeout...")
        resp = requests.post(
            "http://localhost:5000/api/auth/register",
            json={
                "email": f"test-{int(time.time())}@example.com",
                "password": "Test123!",
                "name": "Test"
            },
            timeout=15
        )
        print(f"✅ Register: {resp.status_code}")
        
        if resp.status_code == 201:
            data = resp.json()
            print("✅ Success!")
            print(f"Token: {data.get('access_token', '')[:40]}...")
            break
        elif attempt < 3:
            print(f"⚠️  Got {resp.status_code}: {resp.text[:100]}")
            print("Waiting 5 seconds before retry...")
            time.sleep(5)
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        if attempt < 3:
            print("Waiting 5 seconds before retry...")
            time.sleep(5)
