# Athena Auth Service

Email OTP + Google OAuth microservice for Athena AI

Run locally:

1. Copy `.env.example` → `.env` and fill in values
2. Install dependencies: `npm install`
3. Start: `npm run dev`

API Endpoints:

- `POST /auth/signup` { name, email, password }
- `POST /auth/verify-otp` { email, otp }
- `POST /auth/resend-otp` { email }
- `POST /auth/login` { email, password }
- `GET /auth/google` → redirect to Google
- `GET /auth/google/callback` → Google OAuth callback
- `POST /support/` { user_id?, email, subject, message }

Notes:
- Uses MongoDB (MONGODB_URI), JWT (JWT_SECRET)
- Rate-limits OTP endpoints
- Sends OTP emails using Nodemailer
- Google OAuth via passport-google-oauth20
