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
    db = Depends(get_database)
):
    """
    Screen multiple resumes against a job description
    """
    if not jd_text and not jd_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either jd_text or jd_id must be provided")

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

    results = []
    os.makedirs("uploads/resumes", exist_ok=True)

    for resume_file in resumes:
        try:
            content = await resume_file.read()
            resume_text = resume_screener_service.extract_text_from_pdf(content)

            screening_result, candidate_data = await resume_screener_service.screen_resume(
                jd_text=jd_text,
                resume_text=resume_text
            )

            # Save resume file locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            candidate_name_for_file = (candidate_data.get("name") if isinstance(candidate_data, dict) else "candidate")
            safe_name = candidate_name_for_file.replace(" ", "_")[:120]
            safe_filename = f"{safe_name}_{timestamp}.pdf"
            resume_path = os.path.join("uploads/resumes", safe_filename)
            with open(resume_path, "wb") as f:
                f.write(content)

            resume_doc = {
                "recruiter_id": recruiter_id,
                "jd_id": jd_id,
                "jd_text": jd_text,
                "candidate_name": candidate_data.get("name") if isinstance(candidate_data, dict) else candidate_data,
                "resume_path": resume_path,
                "match_score": int(screening_result.get("match_score", 0)),
                "summary": screening_result.get("summary", ""),
                "status": screening_result.get("status", ""),
                "candidate_data": candidate_data,
                "created_at": datetime.utcnow()
            }

            await db["resumes"].insert_one(resume_doc)

            results.append(ResumeScreenResponse(
                candidate_name=resume_doc["candidate_name"],
                match_score=resume_doc["match_score"],
                summary=resume_doc["summary"],
                status=resume_doc["status"],
                resume_path=resume_doc["resume_path"]
            ))

            logger.info("✅ Screened resume for %s: %s%%", resume_doc["candidate_name"], resume_doc["match_score"])

        except Exception as e:
            logger.error("❌ Error processing resume %s: %s", getattr(resume_file, "filename", "unknown"), e)
            # continue with other resumes

    return BatchScreenResponse(
        results=sorted(results, key=lambda x: x.match_score, reverse=True),
        total_processed=len(results),
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
                "match_score": result["match_score"],
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
            "match_score": result["match_score"],
            "summary": result["summary"],
            "status": result["status"],
            "candidate_data": result["candidate_data"],
            "resume_path": result["resume_path"],
            "created_at": result["created_at"]
        }
    except Exception as e:
        logger.error("❌ Error retrieving resume detail: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve resume detail")
