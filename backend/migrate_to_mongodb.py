#!/usr/bin/env python3
"""
Migration script to import existing users from FastAPI SQLite to MongoDB auth-service
Run: python migrate_to_mongodb.py
"""
import asyncio
import os
import sys
import bcrypt
from datetime import datetime
import httpx

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.core.database import AsyncSessionLocal
from api.models.models import User as SQLUser


async def migrate_users_to_mongodb():
    """Migrate users from SQLite to MongoDB auth-service"""
    
    print("🔄 Starting migration of users to MongoDB auth-service...\n")
    
    # Get users from SQLite
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT * FROM users")
        users = result.scalars().all()
    
    if not users:
        print("⚠️  No users found in SQLite database")
        return
    
    print(f"📊 Found {len(users)} users to migrate\n")
    
    # Prepare MongoDB auth-service client
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:4000")
    
    migrated = 0
    failed = 0
    
    async with httpx.AsyncClient() as client:
        for user in users:
            try:
                # Create user in MongoDB via auth-service
                response = await client.post(
                    f"{auth_service_url}/auth/signup",
                    json={
                        "name": user.name or "Migrated User",
                        "email": user.email,
                        "password": user.password_hash  # Should be hashed already
                    },
                    timeout=10
                )
                
                if response.status_code == 201:
                    # Immediately verify the user since they existed in our system
                    verify_response = await client.post(
                        f"{auth_service_url}/auth/verify-otp",
                        json={"email": user.email, "otp": "000000"},
                        timeout=10
                    )
                    
                    if verify_response.status_code == 200:
                        print(f"✅ Migrated: {user.email}")
                        migrated += 1
                    else:
                        print(f"⚠️  Created but verify failed: {user.email}")
                        migrated += 1
                else:
                    print(f"❌ Failed for {user.email}: {response.json()}")
                    failed += 1
            except Exception as e:
                print(f"❌ Error migrating {user.email}: {str(e)}")
                failed += 1
    
    print(f"\n📈 Migration complete!")
    print(f"   ✅ Migrated: {migrated}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total: {len(users)}\n")


if __name__ == "__main__":
    asyncio.run(migrate_users_to_mongodb())
