"""Resume Screening Data Models (cleaned / pydantic v2 compatible)"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Literal, Annotated
from datetime import datetime
from pydantic.functional_validators import BeforeValidator

# When storing ObjectId from Mongo, we accept str and validate via BeforeValidator
PyObjectId = Annotated[str, BeforeValidator(str)]

class CandidateResume(BaseModel):
    """Structured data extracted from a candidate's resume"""
    name: str = Field(description="The full name of the candidate")
    skills: List[str] = Field(default_factory=list, description="A list of skills possessed by the candidate")
    work_experience: List[Dict] = Field(default_factory=list, description="List of previous work experiences")
    total_experience_years: int = Field(0, description="Total years of professional experience")

class ScreeningResult(BaseModel):
    """The final output of the screening process"""
    match_score: int = Field(description="A score from 0 to 100", ge=0, le=100)
    summary: str = Field(description="Summary explaining the score")
    status: Literal["Strong Match", "Potential Fit", "Not a Fit"] = Field(description="Final recommendation")

class ResumeScreenRequest(BaseModel):
    """Request model for resume screening"""
    jd_id: Optional[str] = Field(None, description="Job Description ID")
    jd_text: Optional[str] = Field(None, description="Job Description text")
    recruiter_id: str = Field(..., description="ID of the recruiter")

class ResumeInDB(BaseModel):
    """Resume screening result in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    recruiter_id: str
    jd_id: Optional[str] = None
    jd_text: Optional[str] = None
    candidate_name: str
    candidate_email: Optional[str] = None
    resume_path: str
    match_score: int
    summary: str
    status: str
    candidate_data: Dict
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResumeScreenResponse(BaseModel):
    """Resume screening response (for API)"""
    candidate_name: str
    match_score: int
    summary: str
    status: str
    resume_path: str

class BatchScreenResponse(BaseModel):
    """Batch screening response"""
    results: List[ResumeScreenResponse]
    total_processed: int
    job_title: Optional[str] = None
