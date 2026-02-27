# Backend

This folder contains all backend server code for the Athena AI platform.

## Structure
- `app.py` - Main Flask application
- `api/` - API endpoints
- `models/` - Database models
- `services/` - Business logic services
- `utils/` - Utility functions
- `config.py` - Configuration settings

## Technologies
- Flask (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Redis (Caching)
- JWT (Authentication)

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables
3. Run the server: `python app.py`

## API Endpoints
- `/api/chat` - Chat with AI
- `/api/auth` - Authentication
- `/api/users` - User management
