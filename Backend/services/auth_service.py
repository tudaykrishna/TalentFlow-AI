"""Authentication Service"""
import os
import secrets
import string
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Tuple
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and User Management Service"""
    
    def __init__(self, db):
        self.db = db
        self.users_collection = db["users"]  # Persistent users (admin/recruiter)
        self.temp_users_collection = db["temp_users"]  # Temporary users (candidates)
    
    # ==================== Password Utilities ====================
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_temp_password(self, length: int = 12) -> str:
        """Generate a random temporary password"""
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def generate_temp_email(self, interview_id: str) -> str:
        """Generate a temporary email for a candidate"""
        random_string = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        return f"candidate_{random_string}_{interview_id[:8]}@talentflow.temp"
    
    # ==================== User Authentication ====================
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """
        Authenticate a user (persistent or temporary)
        Returns user data if authentication is successful, None otherwise
        """
        try:
            # First, try to authenticate as persistent user (admin/recruiter)
            user = await self.users_collection.find_one({"email": email})
            
            if user:
                if self.verify_password(password, user["hashed_password"]):
                    logger.info(f"✅ Persistent user authenticated: {email}")
                    return {
                        "id": str(user["_id"]),
                        "email": user["email"],
                        "username": user.get("username"),
                        "role": user["role"],
                        "user_type": "persistent"
                    }
                else:
                    logger.warning(f"❌ Invalid password for persistent user: {email}")
                    return None
            
            # If not found, try temporary user
            temp_user = await self.temp_users_collection.find_one({"email": email})
            
            if temp_user:
                # Check if password is correct
                if not self.verify_password(password, temp_user["hashed_password"]):
                    logger.warning(f"❌ Invalid password for temporary user: {email}")
                    return None
                
                # Check if account has expired
                if datetime.utcnow() > temp_user["expires_at"]:
                    logger.warning(f"❌ Temporary account expired: {email}")
                    return {
                        "id": str(temp_user["_id"]),
                        "email": temp_user["email"],
                        "role": "user",
                        "user_type": "expired",
                        "error": "account_expired"
                    }
                
                # Check if interview has been attempted
                if temp_user["attempted"]:
                    logger.warning(f"❌ Interview already attempted: {email}")
                    return {
                        "id": str(temp_user["_id"]),
                        "email": temp_user["email"],
                        "role": "user",
                        "user_type": "attempted",
                        "error": "interview_attempted"
                    }
                
                logger.info(f"✅ Temporary user authenticated: {email}")
                return {
                    "id": str(temp_user["_id"]),
                    "email": temp_user["email"],
                    "role": "user",
                    "user_type": "temporary",
                    "interview_id": temp_user["interview_assigned"]
                }
            
            logger.warning(f"❌ User not found: {email}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error authenticating user: {e}")
            raise
    
    # ==================== Persistent User Management ====================
    
    async def create_persistent_user(self, username: str, email: str, password: str, role: str) -> dict:
        """Create a new persistent user (admin/recruiter)"""
        try:
            # Check if user already exists
            existing_user = await self.users_collection.find_one({
                "$or": [{"email": email}, {"username": username}]
            })
            
            if existing_user:
                raise ValueError("User with this email or username already exists")
            
            # Create user document
            user_doc = {
                "username": username,
                "email": email,
                "hashed_password": self.hash_password(password),
                "role": role,
                "created_at": datetime.utcnow()
            }
            
            result = await self.users_collection.insert_one(user_doc)
            user_id = str(result.inserted_id)
            
            logger.info(f"✅ Persistent user created: {email} (Role: {role})")
            
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "created_at": user_doc["created_at"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating persistent user: {e}")
            raise
    
    async def get_persistent_user(self, user_id: str) -> Optional[dict]:
        """Get a persistent user by ID"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["hashed_password"]
            return user
        except Exception as e:
            logger.error(f"❌ Error getting persistent user: {e}")
            return None
    
    # ==================== Temporary User Management ====================
    
    async def create_temp_user(self, interview_id: str) -> Tuple[str, str, str]:
        """
        Create a temporary user for an interview
        Returns: (user_id, email, password)
        """
        try:
            # Generate credentials
            temp_email = self.generate_temp_email(interview_id)
            temp_password = self.generate_temp_password()
            
            # Create temp user document
            temp_user_doc = {
                "email": temp_email,
                "hashed_password": self.hash_password(temp_password),
                "role": "user",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24),
                "interview_assigned": interview_id,
                "attempted": False
            }
            
            result = await self.temp_users_collection.insert_one(temp_user_doc)
            user_id = str(result.inserted_id)
            
            logger.info(f"✅ Temporary user created for interview {interview_id}")
            
            return (user_id, temp_email, temp_password)
            
        except Exception as e:
            logger.error(f"❌ Error creating temporary user: {e}")
            raise
    
    async def create_temp_user_with_username(self, interview_id: str, username: str, candidate_name: str) -> Tuple[str, str, str]:
        """
        Create a temporary user for an interview with custom username
        Returns: (user_id, email, password)
        """
        try:
            # Use username as email if it contains @, otherwise add @talentflow.temp
            if "@" in username:
                temp_email = username
            else:
                temp_email = f"{username}@talentflow.temp"
            
            # Generate password
            temp_password = self.generate_temp_password()
            
            # Create temp user document
            temp_user_doc = {
                "email": temp_email,
                "username": username,
                "full_name": candidate_name,
                "hashed_password": self.hash_password(temp_password),
                "role": "user",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24),
                "interview_assigned": interview_id,
                "attempted": False
            }
            
            result = await self.temp_users_collection.insert_one(temp_user_doc)
            user_id = str(result.inserted_id)
            
            logger.info(f"✅ Temporary user created for {candidate_name} ({username}) - Interview {interview_id}")
            
            return (user_id, temp_email, temp_password)
            
        except Exception as e:
            logger.error(f"❌ Error creating temporary user: {e}")
            raise
    
    async def mark_interview_attempted(self, user_id: str) -> bool:
        """Mark a temporary user's interview as attempted"""
        try:
            result = await self.temp_users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"attempted": True}}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Interview marked as attempted for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error marking interview as attempted: {e}")
            raise
    
    async def get_temp_user(self, user_id: str) -> Optional[dict]:
        """Get a temporary user by ID"""
        try:
            temp_user = await self.temp_users_collection.find_one({"_id": ObjectId(user_id)})
            if temp_user:
                temp_user["id"] = str(temp_user["_id"])
                del temp_user["_id"]
                del temp_user["hashed_password"]
            return temp_user
        except Exception as e:
            logger.error(f"❌ Error getting temporary user: {e}")
            return None
    
    async def cleanup_expired_users(self) -> int:
        """Clean up expired temporary users (can be run as a scheduled task)"""
        try:
            result = await self.temp_users_collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"🗑️ Cleaned up {deleted_count} expired temporary users")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired users: {e}")
            raise

