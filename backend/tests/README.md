# 🧪 Backend Tests

Tests for the Athena AI ChatBot Backend API

## Folder Structure

```
tests/
├── auth/                          # Authentication tests
│   ├── test_auth_flows.py         # Complete auth flow (signup, login, OTP)
│   ├── test_auth_flow_complete.py # Auth → Chatbot creation flow
│   ├── test_auth_flow_fixed.py    # Fixed auth endpoints
│   ├── test_auth_timeout.py       # Auth with timeout handling
│   └── test_otp_send.py           # OTP send/verify flow
│
└── README.md (this file)
```

## Running Tests

### Prerequisites
```bash
# Backend must be running
cd backend
python run.py
# Server will be on http://localhost:5000
```

### Run Auth Tests
```bash
# From backend/ directory
python tests/auth/test_auth_flows.py

python tests/auth/test_auth_flow_complete.py

python tests/auth/test_auth_flow_fixed.py

python tests/auth/test_auth_timeout.py

python tests/auth/test_otp_send.py
```

## Test Descriptions

### `test_auth_flows.py`
Tests password signup, password login, and OTP login flows:
- ✅ Password signup
- ✅ Password login
- ✅ Send OTP (creates OTP-only user)
- ✅ OTP verification
- ✅ Adding password to OTP-only user
- ✅ Login with added password

### `test_auth_flow_complete.py`
Tests complete flow from registration to chatbot creation:
- ✅ User registration
- ✅ Token verification (GET /api/auth/me)
- ✅ Create chatbot
- ✅ Verify token attachment
- ✅ Get chatbot list

### `test_auth_flow_fixed.py`
Tests fixed authentication endpoints

### `test_auth_timeout.py`
Tests authentication with timeout handling

### `test_otp_send.py`
Tests OTP generation and sending:
- ✅ Send OTP via /api/auth/otp/send
- ✅ Retrieve OTP from database
- ✅ Verify OTP timing

## Database Access

These tests connect directly to SQLite database:
```
athena.db
```

To inspect test data:
```bash
sqlite3 athena.db

# View users
SELECT id, email, oauth_provider FROM users;

# View chatbots
SELECT id, owner_id, name FROM chatbots;

# Check OTP (if not cleared)
SELECT email, otp_code, otp_expires_at FROM users WHERE otp_code IS NOT NULL;
```

## Debugging Tests

### Check Backend is Running
```bash
curl http://localhost:5000/docs
```

### Check Database
```bash
sqlite3 backend/athena.db
.tables
SELECT * FROM users LIMIT 5;
```

### View Logs
Look at terminal output where `python run.py` is running

### Clear Test Data
```bash
# Delete test user
sqlite3 backend/athena.db
DELETE FROM users WHERE email LIKE 'test%';

# Or delete all and reset
rm athena.db
# Restart backend to recreate empty tables
```

## Notes

- All tests use relative paths via `Path` object for portability
- Database path: `../../athena.db` from test location
- Tests can run in any order (independent)
- Some tests create data that persists in database

---

**Last Updated:** March 23, 2026
