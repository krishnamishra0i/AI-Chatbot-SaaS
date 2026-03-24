"""
MongoDB configuration for Athena AI
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
from api.core.config import get_settings

settings = get_settings()

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "athena_ai")

# Global MongoDB client and database
mongodb_client = None
mongodb_db = None


async def connect_to_mongo():
    """Initialize MongoDB connection on app startup"""
    global mongodb_client, mongodb_db
    try:
        print(f"[MongoDB] Connecting to {MONGODB_URL}...")
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        mongodb_db = mongodb_client[MONGODB_DATABASE]
        
        # Test connection
        await mongodb_db.command("ping")
        print(f"[MongoDB] ✓ Connected to {MONGODB_DATABASE}")
        
        # Create indexes for OTP collection
        await mongodb_db.users.create_index([("email", 1)], unique=True)
        print("[MongoDB] ✓ Indexes created")
    except Exception as e:
        print(f"[MongoDB] ✗ Connection failed: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection on app shutdown"""
    global mongodb_client
    if mongodb_client:
        print("[MongoDB] Closing connection...")
        mongodb_client.close()
        print("[MongoDB] ✓ Connection closed")


def get_db():
    """Get MongoDB database instance"""
    return mongodb_db
