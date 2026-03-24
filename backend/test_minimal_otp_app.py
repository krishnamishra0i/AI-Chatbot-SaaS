"""
Minimal FastAPI app for MongoDB OTP authentication testing
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

# Set environment variables
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "athena_ai"
os.environ["DEBUG_MODE"] = "true"

from api.core.mongodb import connect_to_mongo, close_mongo_connection
from api.routes import otp_auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting minimal OTP auth server...")
    await connect_to_mongo()
    print("✅ MongoDB connected")
    yield
    print("👋 Shutting down")
    await close_mongo_connection()

# Create minimal app
app = FastAPI(
    title="Athena OTP Auth",
    version="1.0.0",
    lifespan=lifespan,
)

# Include only OTP routes
app.include_router(otp_auth.router)

# Health endpoint
@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "test_minimal_otp_app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
