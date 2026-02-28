Development notes and psycopg2 workaround

If you are developing on Windows and saw errors building `psycopg2-binary`, use the following options:

1) Use the development requirements (no postgres binary build):

   python -m pip install -r requirements-dev.txt

2) If you need Postgres and `psycopg2-binary`, install the Visual Studio Build Tools:
   - Install "Desktop development with C++" workload
   - Then run: python -m pip install -r requirements.txt

3) Docker alternative: run Postgres in Docker and avoid installing `psycopg2-binary` locally.

OAuth notes

- To enable real Google OAuth, set these in `backend/.env`:
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - OAUTH_REDIRECT_BASE (e.g., http://localhost:5174)

- Start endpoint (backend): GET /api/auth/oauth/google/start (returns `auth_url` JSON)
- Callback endpoint (backend): GET /api/auth/oauth/google/callback (exchanges code if credentials set)

Security reminder: The mock auth endpoints are for development only. Implement secure storage, password hashing, and production-grade OAuth handling for real apps.
