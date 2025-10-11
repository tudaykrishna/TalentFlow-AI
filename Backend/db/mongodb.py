"""MongoDB Connection and Database Manager"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB Database Manager"""
    
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "talentflow_db")
        self.client: AsyncIOMotorClient = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Verify connection
            await self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.db_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.db[collection_name]

# Global database instance
mongodb = MongoDB()

async def get_database():
    """Dependency to get database instance"""
    return mongodb.db

