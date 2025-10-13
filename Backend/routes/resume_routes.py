"""Resume Screening API Routes (FastAPI)
Kept the API contract the same but added a few defensive checks and clearer logging.
"""

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
    top_k: int = Form(5),  # Default to top 5
    db = Depends(get_database)
):
    """
    Screen multiple resumes against a job description and return top K most similar candidates.
    
    Args:
        resumes: List of PDF resume files
        jd_text: Job description text (if not using jd_id)
        jd_id: Job description ID from database (if not using jd_text)
        recruiter_id: ID of the recruiter
        top_k: Number of top candidates to return (default: 5)
    
    Returns:
        BatchScreenResponse with top K candidates ranked by similarity
    """
    if not jd_text and not jd_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either jd_text or jd_id must be provided")
    
    if not resumes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one resume file must be uploaded")
    
    # Validate top_k
    if top_k < 1:
        top_k = 5
    if top_k > len(resumes):
        top_k = len(resumes)

    job_title = None
    if jd_id:
        from bson import ObjectId
        try:
            jd = await db["jds"].find_one({"_id": ObjectId(jd_id)})
            if not jd:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
            jd_text = jd.get("generated_content", jd_text)
            job_title = jd.get("job_title")
        except Exception as e:
            logger.error("Error fetching JD: %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch job description")

    # Prepare all resumes for batch processing
    os.makedirs("uploads/resumes", exist_ok=True)
    resumes_data = []
    total_uploaded = len(resumes)
    
    logger.info(f"📤 Processing {total_uploaded} uploaded resumes")
    
    for resume_file in resumes:
        try:
            content = await resume_file.read()
            resume_text = resume_screener_service.extract_text_from_pdf(content)
            
            if not resume_text or len(resume_text.strip()) < 50:
                logger.warning(f"⚠️ Resume {resume_file.filename} has insufficient text, skipping")
                continue
            
            resumes_data.append((resume_file.filename, content, resume_text))
            
        except Exception as e:
            logger.error(f"❌ Error reading resume {resume_file.filename}: %s", e)
            # Continue with other resumes
            continue
    
    if not resumes_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No valid resumes could be processed. Ensure PDFs contain extractable text."
        )
    
    # Rank all resumes and get top K
    try:
        top_candidates = await resume_screener_service.rank_resumes(
            jd_text=jd_text,
            resumes_data=resumes_data,
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"❌ Error ranking resumes: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rank resumes: {str(e)}"
        )
    
    if not top_candidates:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No candidates could be successfully processed and ranked"
        )
    
    # Save top K candidates to database and prepare response
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for candidate in top_candidates:
        try:
            # Save resume file locally
            safe_name = candidate["candidate_name"].replace(" ", "_")[:120]
            safe_filename = f"{safe_name}_{timestamp}_rank{candidate['rank']}.pdf"
            resume_path = os.path.join("uploads/resumes", safe_filename)
            
            with open(resume_path, "wb") as f:
                f.write(candidate["content_bytes"])
            
            # Prepare document for MongoDB
            resume_doc = {
                "recruiter_id": recruiter_id,
                "jd_id": jd_id,
                "jd_text": jd_text,
                "candidate_name": candidate["candidate_name"],
                "resume_path": resume_path,
                "similarity_score": candidate["similarity_score"],
                "rank": candidate["rank"],
                "summary": candidate["summary"],
                "status": candidate["status"],
                "candidate_data": {
                    "name": candidate["candidate_name"],
                    "resume_id": candidate["resume_id"]
                },
                "created_at": datetime.utcnow()
            }
            
            # Insert into database
            await db["resumes"].insert_one(resume_doc)
            
            # Add to response
            results.append(ResumeScreenResponse(
                candidate_name=candidate["candidate_name"],
                similarity_score=candidate["similarity_score"],
                rank=candidate["rank"],
                summary=candidate["summary"],
                status=candidate["status"],
                resume_path=resume_path
            ))
            
            logger.info(
                f"✅ Rank #{candidate['rank']}: {candidate['candidate_name']} "
                f"(similarity: {candidate['similarity_score']:.1f}%)"
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving candidate {candidate['candidate_name']}: %s", e)
            # Continue with other candidates
            continue
    
    logger.info(f"🎯 Successfully ranked and saved top {len(results)} candidates out of {len(resumes_data)} processed")
    
    return BatchScreenResponse(
        results=results,  # Already sorted by rank
        total_uploaded=total_uploaded,
        total_processed=len(resumes_data),
        top_k=len(results),
        job_title=job_title
    )

@router.get("/results/{recruiter_id}")
async def get_screening_results(recruiter_id: str, db = Depends(get_database)):
    try:
        cursor = db["resumes"].find({"recruiter_id": recruiter_id}).sort("created_at", -1)
        results = await cursor.to_list(length=100)
        return [
            {
                "id": str(result["_id"]),
                "candidate_name": result["candidate_name"],
                "similarity_score": result.get("similarity_score", result.get("match_score", 0)),  # Backward compatibility
                "rank": result.get("rank", 0),
                "status": result["status"],
                "created_at": result["created_at"]
            }
            for result in results
        ]
    except Exception as e:
        logger.error("❌ Error retrieving screening results: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve screening results")

@router.get("/detail/{resume_id}")
async def get_resume_detail(resume_id: str, db = Depends(get_database)):
    try:
        from bson import ObjectId
        result = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume screening result not found")
        return {
            "id": str(result["_id"]),
            "candidate_name": result["candidate_name"],
            "similarity_score": result.get("similarity_score", result.get("match_score", 0)),  # Backward compatibility
            "rank": result.get("rank", 0),
            "summary": result["summary"],
            "status": result["status"],
            "candidate_data": result["candidate_data"],
            "resume_path": result["resume_path"],
            "created_at": result["created_at"]
        }
    except Exception as e:
        logger.error("❌ Error retrieving resume detail: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve resume detail")
