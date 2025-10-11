"""
Create Admin/Recruiter Users
Utility script to create persistent users for the system
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    """Interactive user creation"""
    print("=" * 60)
    print("TalentFlow AI - Create User")
    print("=" * 60)
    
    # Get user input
    print("\nEnter user details:")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    print("\nSelect role:")
    print("1. Admin")
    print("2. Recruiter")
    role_choice = input("Enter choice (1/2): ").strip()
    
    role = "admin" if role_choice == "1" else "recruiter"
    
    # Confirm
    print(f"\n--- User Details ---")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Role: {role}")
    
    confirm = input("\nCreate this user? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("User creation cancelled.")
        return
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "talentflow_db")
    
    print(f"\nConnecting to MongoDB: {db_name}")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    try:
        # Check if user already exists
        existing = await db["users"].find_one({
            "$or": [{"email": email}, {"username": username}]
        })
        
        if existing:
            print("❌ Error: User with this email or username already exists!")
            return
        
        # Create user
        user_doc = {
            "username": username,
            "email": email,
            "hashed_password": pwd_context.hash(password),
            "role": role,
            "created_at": datetime.utcnow()
        }
        
        result = await db["users"].insert_one(user_doc)
        
        print(f"\n✅ User created successfully!")
        print(f"User ID: {result.inserted_id}")
        print(f"\nYou can now login with:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_user())

