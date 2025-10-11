"""Resume Screening API Routes"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import List
from models.resume_model import ResumeScreenResponse, BatchScreenResponse
from services.resume_service import resume_screener_service
from db.mongodb import get_database
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["Resume Screening"])

@router.post("/screen", response_model=BatchScreenResponse, status_code=status.HTTP_200_OK)
async def screen_resumes(
    resumes: List[UploadFile] = File(...),
    jd_text: str = Form(None),
    jd_id: str = Form(None),
    recruiter_id: str = Form(...),
    db = Depends(get_database)
):
    """
    Screen multiple resumes against a job description
    
    - **resumes**: List of PDF resume files
    - **jd_text**: Job description text (optional if jd_id is provided)
    - **jd_id**: Job description ID from database (optional if jd_text is provided)
    - **recruiter_id**: ID of the recruiter performing the screening
    """
    try:
        # Get JD text
        if not jd_text and not jd_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either jd_text or jd_id must be provided"
            )
        
        job_title = None
        if jd_id:
            from bson import ObjectId
            jd = await db["jds"].find_one({"_id": ObjectId(jd_id)})
            if not jd:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job description not found"
                )
            jd_text = jd.get("generated_content", jd_text)
            job_title = jd.get("job_title")
        
        results = []
        
        # Create uploads directory
        os.makedirs("uploads/resumes", exist_ok=True)
        
        for resume_file in resumes:
            try:
                # Read resume content
                resume_content = await resume_file.read()
                
                # Extract text from PDF
                resume_text = resume_screener_service.extract_text_from_pdf(resume_content)
                
                # Screen resume
                screening_result, candidate_data = await resume_screener_service.screen_resume(
                    jd_text=jd_text,
                    resume_text=resume_text
                )
                
                # Save resume file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"{candidate_data.name.replace(' ', '_')}_{timestamp}.pdf"
                resume_path = os.path.join("uploads/resumes", safe_filename)
                
                with open(resume_path, "wb") as f:
                    f.write(resume_content)
                
                # Save to database
                resume_doc = {
                    "recruiter_id": recruiter_id,
                    "jd_id": jd_id,
                    "jd_text": jd_text,
                    "candidate_name": candidate_data.name,
                    "resume_path": resume_path,
                    "match_score": screening_result.match_score,
                    "summary": screening_result.summary,
                    "status": screening_result.status,
                    "candidate_data": candidate_data.model_dump(),
                    "created_at": datetime.utcnow()
                }
                
                await db["resumes"].insert_one(resume_doc)
                
                results.append(ResumeScreenResponse(
                    candidate_name=candidate_data.name,
                    match_score=screening_result.match_score,
                    summary=screening_result.summary,
                    status=screening_result.status,
                    resume_path=resume_path
                ))
                
                logger.info(f"✅ Screened resume for {candidate_data.name}: {screening_result.match_score}%")
                
            except Exception as e:
                logger.error(f"❌ Error screening resume {resume_file.filename}: {e}")
                # Continue with other resumes
                continue
        
        logger.info(f"✅ Batch screening completed: {len(results)} resumes processed")
        
        return BatchScreenResponse(
            results=sorted(results, key=lambda x: x.match_score, reverse=True),
            total_processed=len(results),
            job_title=job_title
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in batch screening: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to screen resumes: {str(e)}"
        )

@router.get("/results/{recruiter_id}")
async def get_screening_results(recruiter_id: str, db = Depends(get_database)):
    """Get all screening results for a recruiter"""
    try:
        cursor = db["resumes"].find({"recruiter_id": recruiter_id}).sort("created_at", -1)
        results = await cursor.to_list(length=100)
        
        return [
            {
                "id": str(result["_id"]),
                "candidate_name": result["candidate_name"],
                "match_score": result["match_score"],
                "status": result["status"],
                "created_at": result["created_at"]
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"❌ Error retrieving screening results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve screening results: {str(e)}"
        )

@router.get("/detail/{resume_id}")
async def get_resume_detail(resume_id: str, db = Depends(get_database)):
    """Get detailed screening result for a specific resume"""
    try:
        from bson import ObjectId
        result = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume screening result not found"
            )
        
        return {
            "id": str(result["_id"]),
            "candidate_name": result["candidate_name"],
            "match_score": result["match_score"],
            "summary": result["summary"],
            "status": result["status"],
            "candidate_data": result["candidate_data"],
            "resume_path": result["resume_path"],
            "created_at": result["created_at"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving resume detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resume detail: {str(e)}"
        )

