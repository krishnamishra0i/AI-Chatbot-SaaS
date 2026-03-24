"""
Auth Flow Test - OTP Login (Send OTP)
Tests the OTP generation and sending flow via /api/auth/otp/send
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

def main():
    print_section("OTP LOGIN FLOW TEST")
    
    email = "testuser@example.com"
    
    # ─────────────────────────────────────────────────────────────────
    # TEST 1: Send OTP
    # ─────────────────────────────────────────────────────────────────
    
    print_section("TEST 1: Send OTP")
    send_otp_data = {"email": email}
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/otp/send", json=send_otp_data, timeout=5)
        print(f"[*] POST /api/auth/otp/send")
        print(f"    Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            msg = data.get('message')
            print(f"    [✓] OTP sent: {msg}")
            
            # Get OTP from DB
            time.sleep(1)
            otp_code = get_otp_from_db(email)
            if otp_code:
                print(f"    [✓] OTP code from DB: {otp_code}")
                return otp_code, email
            else:
                print(f"    [✗] Could not retrieve OTP from DB")
                return None, None
        else:
            print(f"    [✗] Error: {res.json()}")
            return None, None
    except Exception as e:
        print(f"    [✗] Exception: {e}")
        return None, None

if __name__ == "__main__":
    otp_code, test_email = main()
    if otp_code:
        print(f"\n[✓] Ready to test OTP verification with code: {otp_code}")
    else:
        print(f"\n[✗] Failed to send OTP")
