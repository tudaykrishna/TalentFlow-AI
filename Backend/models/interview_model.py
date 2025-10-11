"""AI Interview Data Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Literal, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator

# Pydantic v2 compatible ObjectId handling
PyObjectId = Annotated[str, BeforeValidator(str)]

class InterviewAssignmentRequest(BaseModel):
    """Request to assign interview to a candidate"""
    candidate_name: str = Field(..., description="Candidate's full name")
    candidate_username: str = Field(..., description="Candidate's username/email")
    jd_id: str = Field(..., description="Job Description ID")
    recruiter_id: str = Field(..., description="Recruiter ID")
    max_questions: int = Field(default=5, description="Number of questions in interview")

class InterviewPlan(BaseModel):
    """Interview plan with topics"""
    topics: List[str] = Field(description="List of key topics to cover")

class Question(BaseModel):
    """Interview question"""
    question: str = Field(description="The interview question")

class Evaluation(BaseModel):
    """Evaluation of candidate's answer"""
    rating: int = Field(description="Rating from 1-5", ge=1, le=5)
    feedback: str = Field(description="Feedback on the answer")

class InterviewSummary(BaseModel):
    """Final interview summary"""
    recommendation: Literal["Proceed", "Hold", "Reject"] = Field(description="Hiring recommendation")
    summary_text: str = Field(description="Comprehensive summary")

class InterviewInDB(BaseModel):
    """Interview session in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    candidate_name: str = Field(..., description="Candidate's full name")
    candidate_username: str = Field(..., description="Candidate's username/email")
    jd_id: str
    recruiter_id: str
    status: Literal["Assigned", "In Progress", "Completed", "Cancelled"] = Field(default="Assigned")
    interview_plan: Optional[List[str]] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    evaluations: List[Dict] = Field(default_factory=list)
    final_summary: Optional[Dict] = None
    max_questions: int = Field(default=5)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewResponse(BaseModel):
    """Interview response model"""
    id: str
    user_id: str
    jd_id: str
    status: str
    created_at: datetime
    
class InterviewStatusResponse(BaseModel):
    """Interview status response"""
    interview_id: str
    status: str
    current_question: Optional[str] = None
    questions_completed: int
    total_questions: int

