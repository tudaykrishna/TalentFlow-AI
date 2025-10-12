"""
Create Default Admin User
Simple script to create a default admin user for first-time setup
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_default_admin():
    """Create a default admin user"""
    print("Creating default admin user...")
    
    # Default admin credentials
    username = "admin"
    email = "admin"
    password = "admin"
    role = "admin"
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "talentflow_db")
    
    print(f"Connecting to MongoDB: {db_name}")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    try:
        # Check if admin already exists
        existing = await db["users"].find_one({"email": email})
        
        if existing:
            print("✅ Admin user already exists!")
            print(f"Email: {email}")
            print(f"Password: {password}")
            return
        
        # Create admin user
        user_doc = {
            "username": username,
            "email": email,
            "hashed_password": pwd_context.hash(password),
            "role": role,
            "created_at": datetime.utcnow()
        }
        
        result = await db["users"].insert_one(user_doc)
        
        print("✅ Default admin user created successfully!")
        print(f"User ID: {result.inserted_id}")
        print(f"\n🔐 Login Credentials:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"\n⚠️  IMPORTANT: Change this password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_default_admin())
