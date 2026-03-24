#!/usr/bin/env python3
"""
Test backend login endpoint with proper response format.
Updated for backend/tests/auth location
"""

import requests
import json
import time

email = f"test_{int(time.time())}@example.com"
password = "testpass123"

print('=== Testing Backend Auth Flow ===\n')

# Step 1: Register
print(f'STEP 1: Register new user ({email})')
response = requests.post(
    'http://localhost:5000/api/auth/register',
    json={'email': email, 'password': password, 'name': 'Test User'},
    timeout=5
)
print(f'Status: {response.status_code}')
if response.status_code == 201:
    data = response.json()
    print(f'✓ Registration successful!')
    print(f'  Response keys: {list(data.keys())}')
    print(f'  access_token: {data.get("access_token", "MISSING")[:30]}...')
    print(f'  user: {data.get("user", {})}')
    token = data.get('access_token')
else:
    print(f'✗ Failed: {response.json()}')
    exit(1)

print()

# Step 2: Login with same credentials
print(f'STEP 2: Login with credentials ({email})')
response = requests.post(
    'http://localhost:5000/api/auth/login',
    json={'email': email, 'password': password},
    timeout=5
)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'✓ Login successful!')
    print(f'  Response keys: {list(data.keys())}')
    print(f'  access_token: {data.get("access_token", "MISSING")[:30]}...')
    print(f'  user email: {data.get("user", {}).get("email")}')
    token = data.get('access_token')
else:
    print(f'✗ Failed: {response.json()}')
    exit(1)

print()

# Step 3: Test that token works for API calls
print('STEP 3: Use token to get profile')
response = requests.get(
    'http://localhost:5000/api/auth/me',
    headers={'Authorization': f'Bearer {token}'},
    timeout=5
)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'✓ Token works!')
    print(f'  User: {data.get("email")}')
else:
    print(f'✗ Failed: {response.json()}')
    exit(1)

print('\n✅ All tests passed!')
