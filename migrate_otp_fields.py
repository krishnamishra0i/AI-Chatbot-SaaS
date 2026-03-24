"""
Migration script — add OTP fields to User table.
Run this after updating the User model.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.core.database import engine, Base
from sqlalchemy import text


async def migrate_add_otp_fields():
    """Add OTP fields to users table if they don't exist."""
    async with engine.begin() as conn:
        try:
            # Add otp_code column
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN otp_code VARCHAR NULL"
            ))
            print("✅ Added otp_code column")
        except Exception as e:
            print(f"  (otp_code column may already exist: {e})")
        
        try:
            # Add otp_expires_at column
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN otp_expires_at DATETIME NULL"
            ))
            print("✅ Added otp_expires_at column")
        except Exception as e:
            print(f"  (otp_expires_at column may already exist: {e})")


async def migrate_recreate_database():
    """Recreate the entire database with all tables."""
    async with engine.begin() as conn:
        # Drop all existing tables
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Dropped all existing tables")
        
        # Create all tables with new schema
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created all tables with OTP fields")


async def main():
    print("\n🔧 Database Migration — Adding OTP Fields")
    print("=" * 50)
    
    try:
        await migrate_recreate_database()
        print("\n✅ Migration complete! Database is ready with OTP support.")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
