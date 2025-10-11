"""Job Description Data Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator

# Pydantic v2 compatible ObjectId handling
PyObjectId = Annotated[str, BeforeValidator(str)]

class JDGenerateRequest(BaseModel):
    """Request model for JD generation"""
    job_title: str = Field(..., description="Job title")
    company_tone: str = Field(default="Professional yet approachable", description="Company tone")
    responsibilities: str = Field(..., description="Key responsibilities")
    skills: str = Field(..., description="Required skills")
    experience: str = Field(..., description="Years of experience required")
    recruiter_id: str = Field(..., description="ID of the recruiter creating the JD")

class JDInDB(BaseModel):
    """Job Description in Database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    job_title: str
    company_tone: str
    responsibilities: str
    skills: str
    experience: str
    recruiter_id: str
    generated_content: str
    pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class JDResponse(BaseModel):
    """JD Response Model"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    job_title: str
    generated_content: str
    pdf_path: Optional[str] = None
    created_at: datetime

