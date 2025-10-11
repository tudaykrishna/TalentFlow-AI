"""AI Interview API Routes"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from models.interview_model import (
    InterviewAssignmentRequest,
    InterviewResponse,
    InterviewStatusResponse
)
from services.interview_service import interview_service
from services.auth_service import AuthService
from services.whisper_service import whisper_service
from db.mongodb import get_database
from datetime import datetime
from bson import ObjectId
import logging
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interview", tags=["AI Interview"])


async def get_auth_service(db = Depends(get_database)):
    """Dependency to get auth service"""
    return AuthService(db)

@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_interview(
    request: InterviewAssignmentRequest, 
    db = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Assign an AI interview to a candidate
    
    - **candidate_name**: Candidate's full name
    - **candidate_username**: Candidate's username/email for login
    - **jd_id**: Job description ID
    - **recruiter_id**: ID of the recruiter assigning the interview
    - **max_questions**: Number of questions in the interview (default: 5)
    
    This endpoint creates a temporary user account for the candidate based on provided username
    and returns the login credentials.
    """
    try:
        # Verify JD exists
        jd = await db["jds"].find_one({"_id": ObjectId(request.jd_id)})
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )
        
        # Create interview assignment first (without user_id)
        interview_doc = {
            "user_id": None,  # Will be updated after creating temp user
            "candidate_name": request.candidate_name,
            "candidate_username": request.candidate_username,
            "jd_id": request.jd_id,
            "recruiter_id": request.recruiter_id,
            "status": "Assigned",
            "interview_plan": None,
            "conversation_history": [],
            "evaluations": [],
            "final_summary": None,
            "max_questions": request.max_questions,
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db["interviews"].insert_one(interview_doc)
        interview_id = str(result.inserted_id)
        
        # Create temporary user for this interview using candidate's username
        temp_user_id, temp_email, temp_password = await auth_service.create_temp_user_with_username(
            interview_id, 
            request.candidate_username,
            request.candidate_name
        )
        
        # Update interview with user_id
        await db["interviews"].update_one(
            {"_id": ObjectId(interview_id)},
            {"$set": {"user_id": temp_user_id}}
        )
        
        logger.info(f"✅ Interview {interview_id} assigned to {request.candidate_name} ({request.candidate_username})")
        
        return {
            "id": interview_id,
            "user_id": temp_user_id,
            "candidate_name": request.candidate_name,
            "candidate_username": request.candidate_username,
            "jd_id": request.jd_id,
            "status": "Assigned",
            "created_at": interview_doc["created_at"],
            "candidate_credentials": {
                "name": request.candidate_name,
                "email": temp_email,
                "password": temp_password,
                "valid_for": "24 hours",
                "message": "Share these credentials with the candidate. They can only attempt the interview once."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error assigning interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign interview: {str(e)}"
        )

@router.post("/{interview_id}/start")
async def start_interview(interview_id: str, db = Depends(get_database)):
    """Start an interview and generate the interview plan"""
    try:
        # Get interview
        interview = await db["interviews"].find_one({"_id": ObjectId(interview_id)})
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        if interview["status"] != "Assigned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interview is already {interview['status']}"
            )
        
        # Get JD
        jd = await db["jds"].find_one({"_id": ObjectId(interview["jd_id"])})
        job_description = jd.get("generated_content", "")
        
        # Generate interview plan
        interview_plan = await interview_service.generate_interview_plan(job_description)
        
        # Generate first question
        first_question = await interview_service.generate_question(
            interview_plan=interview_plan,
            conversation_history=[],
            evaluations=[]
        )
        
        # Update interview
        await db["interviews"].update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": {
                    "status": "In Progress",
                    "interview_plan": interview_plan,
                    "started_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"✅ Interview {interview_id} started")
        
        return {
            "interview_id": interview_id,
            "status": "In Progress",
            "current_question": first_question,
            "question_number": 1,
            "total_questions": interview["max_questions"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error starting interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}"
        )

@router.post("/{interview_id}/answer")
async def submit_answer(interview_id: str, answer: str, db = Depends(get_database)):
    """Submit an answer and get the next question or summary"""
    try:
        # Get interview
        interview = await db["interviews"].find_one({"_id": ObjectId(interview_id)})
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        if interview["status"] != "In Progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview is not in progress"
            )
        
        # Get current question from conversation history or generate first one
        conversation_history = interview.get("conversation_history", [])
        evaluations = interview.get("evaluations", [])
        interview_plan = interview.get("interview_plan", [])
        
        # Determine current question
        if len(evaluations) < len(conversation_history):
            # There's an unanswered question
            current_question = conversation_history[-1]["question"]
        else:
            # Generate next question
            current_question = await interview_service.generate_question(
                interview_plan=interview_plan,
                conversation_history=conversation_history,
                evaluations=evaluations
            )
        
        # Evaluate answer
        evaluation = await interview_service.evaluate_answer(current_question, answer)
        
        # Add to conversation history and evaluations
        conversation_history.append({"question": current_question, "answer": answer})
        evaluations.append(evaluation)
        
        # Check if interview is complete
        if len(evaluations) >= interview["max_questions"]:
            # Generate summary
            summary = await interview_service.summarize_interview(
                conversation_history=conversation_history,
                evaluations=evaluations
            )
            
            # Update interview as completed
            await db["interviews"].update_one(
                {"_id": ObjectId(interview_id)},
                {
                    "$set": {
                        "status": "Completed",
                        "conversation_history": conversation_history,
                        "evaluations": evaluations,
                        "final_summary": summary,
                        "completed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Mark temporary user as attempted
            user_id = interview.get("user_id")
            if user_id:
                auth_service = AuthService(db)
                await auth_service.mark_interview_attempted(user_id)
            
            logger.info(f"✅ Interview {interview_id} completed")
            
            return {
                "interview_id": interview_id,
                "status": "Completed",
                "summary": summary,
                "questions_completed": len(evaluations),
                "total_questions": interview["max_questions"]
            }
        else:
            # Generate next question
            next_question = await interview_service.generate_question(
                interview_plan=interview_plan,
                conversation_history=conversation_history,
                evaluations=evaluations
            )
            
            # Update interview
            await db["interviews"].update_one(
                {"_id": ObjectId(interview_id)},
                {
                    "$set": {
                        "conversation_history": conversation_history,
                        "evaluations": evaluations,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "interview_id": interview_id,
                "status": "In Progress",
                "current_question": next_question,
                "evaluation": evaluation,
                "questions_completed": len(evaluations),
                "total_questions": interview["max_questions"]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )

@router.get("/{interview_id}/status", response_model=InterviewStatusResponse)
async def get_interview_status(interview_id: str, db = Depends(get_database)):
    """Get the current status of an interview"""
    try:
        interview = await db["interviews"].find_one({"_id": ObjectId(interview_id)})
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        conversation_history = interview.get("conversation_history", [])
        current_question = None
        
        if interview["status"] == "In Progress" and len(conversation_history) > 0:
            current_question = conversation_history[-1].get("question")
        
        return InterviewStatusResponse(
            interview_id=interview_id,
            status=interview["status"],
            current_question=current_question,
            questions_completed=len(interview.get("evaluations", [])),
            total_questions=interview["max_questions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting interview status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview status: {str(e)}"
        )

@router.get("/user/{user_id}")
async def get_user_interviews(user_id: str, db = Depends(get_database)):
    """Get all interviews assigned to a user"""
    try:
        cursor = db["interviews"].find({"user_id": user_id}).sort("created_at", -1)
        interviews = await cursor.to_list(length=100)
        
        return [
            {
                "id": str(interview["_id"]),
                "jd_id": interview["jd_id"],
                "status": interview["status"],
                "created_at": interview["created_at"],
                "started_at": interview.get("started_at"),
                "completed_at": interview.get("completed_at")
            }
            for interview in interviews
        ]
        
    except Exception as e:
        logger.error(f"❌ Error retrieving user interviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interviews: {str(e)}"
        )

@router.get("/{interview_id}/summary")
async def get_interview_summary(interview_id: str, db = Depends(get_database)):
    """Get the final summary of a completed interview"""
    try:
        interview = await db["interviews"].find_one({"_id": ObjectId(interview_id)})
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        if interview["status"] != "Completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview is not completed yet"
            )
        
        return {
            "interview_id": interview_id,
            "final_summary": interview.get("final_summary"),
            "conversation_history": interview.get("conversation_history"),
            "evaluations": interview.get("evaluations"),
            "completed_at": interview.get("completed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving interview summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview summary: {str(e)}"
        )

@router.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe audio to text using Local Whisper (GPU-only)
    
    - **audio_file**: Audio file in WAV, MP3, or other supported format
    
    Uses:
    - Local Whisper medium model on RTX 3060 GPU
    - No API calls, no cost
    - ~0.3s processing time (6.7x faster than API)
    
    Returns the transcribed text with metadata
    """
    try:
        # Check if GPU is available
        if not whisper_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GPU not available. Local Whisper requires CUDA-enabled GPU."
            )
        
        logger.info("🎙️  Transcribing with local Whisper (GPU)")
        
        # Read audio file
        audio_data = await audio_file.read()
        
        # Time the transcription
        import time
        start_time = time.time()
        
        # Transcribe using local Whisper
        transcribed_text, metadata = await whisper_service.transcribe_upload(
            audio_data, 
            audio_file.filename or "audio.wav"
        )
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Local GPU transcription successful ({processing_time:.2f}s)")
        logger.info(f"   Language: {metadata['language']} ({metadata['language_probability']:.1%})")
        logger.info(f"   Speed: {metadata['duration'] / metadata['processing_time']:.1f}x realtime")
        
        return {
            "text": transcribed_text,
            "status": "success",
            "method": "local_gpu",
            "processing_time": round(processing_time, 2),
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Local Whisper transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

@router.get("/whisper/health")
async def whisper_health_check():
    """
    Check Local Whisper service health and availability
    
    Returns status of local GPU transcription
    """
    try:
        status_info = whisper_service.get_status()
        
        return {
            "service": "LocalWhisper",
            "status": "available" if status_info["available"] else "unavailable",
            **status_info
        }
    except Exception as e:
        logger.error(f"Error checking Whisper health: {e}")
        return {
            "service": "LocalWhisper",
            "status": "error",
            "error": str(e)
        }

@router.get("/recruiter/{recruiter_id}/results")
async def get_recruiter_interview_results(recruiter_id: str, db = Depends(get_database)):
    """Get all interview results for a recruiter"""
    try:
        # Fetch all interviews assigned by this recruiter
        cursor = db["interviews"].find({
            "recruiter_id": recruiter_id,
            "status": "Completed"
        }).sort("completed_at", -1)
        
        interviews = await cursor.to_list(length=100)
        
        results = []
        for interview in interviews:
            # Get user details
            user = await db["users"].find_one({"_id": interview.get("user_id")})
            
            # Get JD details
            jd = await db["jds"].find_one({"_id": ObjectId(interview["jd_id"])})
            
            # Calculate average score
            evaluations = interview.get("evaluations", [])
            avg_score = sum([e.get("rating", 0) for e in evaluations]) / len(evaluations) if evaluations else 0
            
            results.append({
                "interview_id": str(interview["_id"]),
                "candidate_name": interview.get("candidate_name", "Unknown"),
                "candidate_username": interview.get("candidate_username", "N/A"),
                "job_title": jd.get("job_title", "Unknown") if jd else "Unknown",
                "status": interview["status"],
                "average_score": round(avg_score, 2),
                "total_questions": len(evaluations),
                "recommendation": interview.get("final_summary", {}).get("recommendation", "N/A"),
                "completed_at": interview.get("completed_at"),
                "created_at": interview.get("created_at")
            })
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error retrieving interview results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview results: {str(e)}"
        )

