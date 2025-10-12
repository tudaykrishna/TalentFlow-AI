#!/bin/bash

# ================================
# TalentFlow AI - Startup Script
# Creates default users and starts the application
# ================================

echo "🚀 Starting TalentFlow AI Backend..."

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
until python -c "
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_mongo():
    try:
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_uri)
        await client.admin.command('ping')
        client.close()
        return True
    except:
        return False

if asyncio.run(check_mongo()):
    print('✅ MongoDB is ready!')
    exit(0)
else:
    print('❌ MongoDB not ready yet...')
    exit(1)
" 2>/dev/null; do
    echo "⏳ Still waiting for MongoDB..."
    sleep 2
done

echo "✅ MongoDB is ready!"

# Create default users
echo "👤 Creating default users..."

# Create admin user
python -c "
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

async def create_admin():
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'talentflow_db')
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # Check if admin exists
    existing = await db['users'].find_one({'email': 'admin'})
    if not existing:
        user_doc = {
            'username': 'admin',
            'email': 'admin',
            'hashed_password': pwd_context.hash('admin'),
            'role': 'admin',
            'created_at': datetime.utcnow()
        }
        await db['users'].insert_one(user_doc)
        print('✅ Admin user created: admin / admin')
    else:
        print('✅ Admin user already exists')
    
    client.close()

asyncio.run(create_admin())
"

# Create recruiter user
python -c "
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

async def create_recruiter():
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'talentflow_db')
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # Check if recruiter exists
    existing = await db['users'].find_one({'email': 'udayt2003@gmail.com'})
    if not existing:
        user_doc = {
            'username': 'recruiter',
            'email': 'udayt2003@gmail.com',
            'hashed_password': pwd_context.hash('Uday@186186'),
            'role': 'recruiter',
            'created_at': datetime.utcnow()
        }
        await db['users'].insert_one(user_doc)
        print('✅ Recruiter user created: udayt2003@gmail.com / Uday@186186')
    else:
        print('✅ Recruiter user already exists')
    
    client.close()

asyncio.run(create_recruiter())
"

echo "🎉 Default users created successfully!"
echo ""
echo "🔐 Login Credentials:"
echo "  Admin: admin / admin"
echo "  Recruiter: udayt2003@gmail.com / Uday@186186"
echo ""

# Start the main application
echo "🚀 Starting FastAPI application..."
exec python main.py
