"""User Data Models"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Literal, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator

# Pydantic v2 compatible ObjectId handling
PyObjectId = Annotated[str, BeforeValidator(str)]

# ==================== Authentication Models ====================

class LoginRequest(BaseModel):
    """Login Request Model"""
    email: str = Field(..., description="Email or username")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    """Login Response Model"""
    user_id: str
    email: str
    username: Optional[str] = None
    role: Literal["user", "recruiter", "admin"]
    message: str

class TokenData(BaseModel):
    """Token Data Model"""
    user_id: str
    email: str
    role: str

# ==================== User Models (Admin/Recruiter) ====================

class PersistentUserBase(BaseModel):
    """Base Model for Admin/Recruiter Users"""
    username: str = Field(..., min_length=3, description="Unique username")
    email: EmailStr = Field(..., description="Email address")
    role: Literal["admin", "recruiter"] = Field(..., description="User role")

class PersistentUserCreate(PersistentUserBase):
    """Model for creating persistent users"""
    password: str = Field(..., min_length=8, description="User password")

class PersistentUserInDB(PersistentUserBase):
    """Persistent User in Database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PersistentUserResponse(BaseModel):
    """Persistent User Response"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    username: str
    email: str
    role: Literal["admin", "recruiter"]
    created_at: datetime

# ==================== Temporary User Models (Candidates) ====================

class TempUserBase(BaseModel):
    """Base Model for Temporary Users (Candidates)"""
    email: EmailStr = Field(..., description="Temporary email address")
    role: Literal["user"] = Field(default="user", description="User role")

class TempUserCreate(TempUserBase):
    """Model for creating temporary users"""
    password: str = Field(..., min_length=8, description="Temporary password")
    interview_assigned: str = Field(..., description="Interview ID assigned to this user")

class TempUserInDB(TempUserBase):
    """Temporary User in Database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Expiration timestamp (24 hours from creation)")
    interview_assigned: str = Field(..., description="Interview ID")
    attempted: bool = Field(default=False, description="Whether the interview has been attempted")

class TempUserResponse(BaseModel):
    """Temporary User Response"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    email: str
    role: Literal["user"]
    created_at: datetime
    expires_at: datetime
    interview_assigned: str
    attempted: bool

