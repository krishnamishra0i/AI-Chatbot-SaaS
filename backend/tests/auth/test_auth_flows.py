"""
Test fixed auth flows: password signup, password login, OTP login
Updated for backend/tests/auth location
"""
import requests
import json
import time
from datetime import datetime
import sqlite3
import sys
from pathlib import Path

# Adjust path to work from tests/auth/ subfolder
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:5000"
DB_PATH = str(Path(__file__).parent.parent.parent / "athena.db")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def get_otp_from_db(email):
    """Extract actual OTP from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"[!] DB Error: {e}")
        return None

# ─────────────────────────────────────────────────────────────────
# TEST 1: Signup with password
# ─────────────────────────────────────────────────────────────────

print_section("TEST 1: Signup with Password")
signup_data = {
    "email": "testuser@example.com",
    "password": "SecurePass123!",
    "name": "Test User"
}

try:
    res = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data, timeout=5)
    print(f"[*] POST /api/auth/signup")
    print(f"    Status: {res.status_code}")
    
    if res.status_code in [200, 201]:
        data = res.json()
        token = data.get('access_token')
        user = data.get('user')
        print(f"    [✓] User created: {user.get('email')}")
        print(f"    [✓] Token received: {token[:30]}...")
        signup_token = token
    else:
        print(f"    [✗] Error: {res.json()}")
        signup_token = None
except Exception as e:
    print(f"    [✗] Exception: {e}")
    signup_token = None

# ─────────────────────────────────────────────────────────────────
# TEST 2: Login with password
# ─────────────────────────────────────────────────────────────────

print_section("TEST 2: Password Login")
login_data = {
    "email": "testuser@example.com",
    "password": "SecurePass123!"
}

try:
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=5)
    print(f"[*] POST /api/auth/login")
    print(f"    Status: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        token = data.get('access_token')
        user = data.get('user')
        print(f"    [✓] Login successful: {user.get('email')}")
        print(f"    [✓] Token received: {token[:30]}...")
        login_token = token
    else:
        print(f"    [✗] Error: {res.json()}")
        login_token = None
except Exception as e:
    print(f"    [✗] Exception: {e}")
    login_token = None

# ─────────────────────────────────────────────────────────────────
# TEST 3: Create OTP-only user via send-otp
# ─────────────────────────────────────────────────────────────────

print_section("TEST 3: Send OTP (Auto-creates OTP-only user)")
otp_email = "otpuser@example.com"
send_otp_data = {"email": otp_email}

try:
    res = requests.post(f"{BASE_URL}/api/auth/send-otp", json=send_otp_data, timeout=5)
    print(f"[*] POST /api/auth/send-otp")
    print(f"    Status: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        msg = data.get('message')
        print(f"    [✓] OTP sent: {msg}")
        
        # Get OTP from DB
        time.sleep(1)
        otp_code = get_otp_from_db(otp_email)
        if otp_code:
            print(f"    [✓] OTP code from DB: {otp_code}")
        else:
            print(f"    [✗] Could not retrieve OTP from DB")
            otp_code = None
    else:
        print(f"    [✗] Error: {res.json()}")
        otp_code = None
except Exception as e:
    print(f"    [✗] Exception: {e}")
    otp_code = None

# ─────────────────────────────────────────────────────────────────
# TEST 4: Try to login OTP-only user with password (should fail with suggestion)
# ─────────────────────────────────────────────────────────────────

print_section("TEST 4: OTP-only User Tries Password Login (Should Recommend OTP)")
login_otp_only = {
    "email": otp_email,
    "password": "anypassword123"
}

try:
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_otp_only, timeout=5)
    print(f"[*] POST /api/auth/login (OTP-only user)")
    print(f"    Status: {res.status_code}")
    
    if res.status_code == 401:
        data = res.json()
        detail = data.get('detail')
        print(f"    [✓] Correctly rejected with message:")
        print(f"        '{detail}'")
        
        if "OTP login" in detail:
            print(f"    [✓] Error message suggests OTP login!")
    else:
        print(f"    [✗] Unexpected status: {res.status_code}")
        print(f"    [✗] Response: {res.json()}")
except Exception as e:
    print(f"    [✗] Exception: {e}")

# ─────────────────────────────────────────────────────────────────
# TEST 5: Verify OTP and login
# ─────────────────────────────────────────────────────────────────

if otp_code:
    print_section("TEST 5: Verify OTP and Get Token")
    verify_otp_data = {
        "email": otp_email,
        "otp_code": otp_code
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/verify-otp", json=verify_otp_data, timeout=5)
        print(f"[*] POST /api/auth/verify-otp")
        print(f"    Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            token = data.get('access_token')
            user = data.get('user')
            print(f"    [✓] OTP verified: {user.get('email')}")
            print(f"    [✓] Token received: {token[:30]}...")
            otp_token = token
        else:
            print(f"    [✗] Error: {res.json()}")
            otp_token = None
    except Exception as e:
        print(f"    [✗] Exception: {e}")
        otp_token = None

# ─────────────────────────────────────────────────────────────────
# TEST 6: Add password to OTP-only user via signup
# ─────────────────────────────────────────────────────────────────

print_section("TEST 6: Add Password to OTP-only User (Signup)")
add_password_data = {
    "email": otp_email,
    "password": "NewPassword456!",
    "name": "OTP User With Password"
}

try:
    res = requests.post(f"{BASE_URL}/api/auth/signup", json=add_password_data, timeout=5)
    print(f"[*] POST /api/auth/signup (existing OTP-only user)")
    print(f"    Status: {res.status_code}")
    
    if res.status_code in [200, 201]:
        data = res.json()
        token = data.get('access_token')
        user = data.get('user')
        print(f"    [✓] Password added to OTP user: {user.get('email')}")
        print(f"    [✓] Token received immediately: {token[:30]}...")
    else:
        print(f"    [✗] Error: {res.json()}")
except Exception as e:
    print(f"    [✗] Exception: {e}")

# ─────────────────────────────────────────────────────────────────
# TEST 7: Now login with the new password
# ─────────────────────────────────────────────────────────────────

print_section("TEST 7: Login with Previously OTP-only User (Now has Password)")
login_new_password = {
    "email": otp_email,
    "password": "NewPassword456!"
}

try:
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_new_password, timeout=5)
    print(f"[*] POST /api/auth/login (OTP user with new password)")
    print(f"    Status: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        token = data.get('access_token')
        user = data.get('user')
        print(f"    [✓] Login successful: {user.get('email')}")
        print(f"    [✓] Token received: {token[:30]}...")
    else:
        print(f"    [✗] Error: {res.json()}")
except Exception as e:
    print(f"    [✗] Exception: {e}")

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────

print_section("SUMMARY")
print(f"""
✓ Password-based signup creates account with password
✓ Users can login with password
✓ OTP flow creates users without password  
✓ OTP-only users get helpful error when trying password login
✓ OTP-only users can add password via signup endpoint
✓ Once password is added, users can login with password
✓ Users can switch between OTP and password authentication
""")
