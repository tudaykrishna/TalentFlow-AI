"""Job Description API Routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from models.jd_model import JDGenerateRequest, JDResponse, JDInDB
from services.jd_service import jd_service
from db.mongodb import get_database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jd", tags=["Job Description"])

@router.post("/generate", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
async def generate_job_description(request: JDGenerateRequest, db = Depends(get_database)):
    """
    Generate a job description based on provided parameters
    
    - **job_title**: Title of the position
    - **company_tone**: Tone of the company (e.g., "Professional yet approachable")
    - **responsibilities**: Key responsibilities
    - **skills**: Required skills
    - **experience**: Years of experience required
    - **recruiter_id**: ID of the recruiter creating the JD
    """
    try:
        # Generate JD content
        jd_content = await jd_service.generate_jd(
            job_title=request.job_title,
            company_tone=request.company_tone,
            responsibilities=request.responsibilities,
            skills=request.skills,
            experience=request.experience
        )
        
        # Save to PDF
        # Sanitize job title for filename (remove invalid characters)
        safe_title = request.job_title.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        pdf_filename = f"jd_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = jd_service.save_jd_to_pdf(jd_content, pdf_filename)
        
        # Save to database
        jd_doc = {
            "job_title": request.job_title,
            "company_tone": request.company_tone,
            "responsibilities": request.responsibilities,
            "skills": request.skills,
            "experience": request.experience,
            "recruiter_id": request.recruiter_id,
            "generated_content": jd_content,
            "pdf_path": pdf_path,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db["jds"].insert_one(jd_doc)
        jd_id = str(result.inserted_id)
        
        logger.info(f"✅ JD created successfully with ID: {jd_id}")
        
        return JDResponse(
            id=jd_id,
            job_title=request.job_title,
            generated_content=jd_content,
            pdf_path=pdf_path,
            created_at=jd_doc["created_at"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating JD: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate job description: {str(e)}"
        )

@router.get("/{jd_id}", response_model=JDResponse)
async def get_job_description(jd_id: str, db = Depends(get_database)):
    """Get a job description by ID"""
    try:
        from bson import ObjectId
        jd = await db["jds"].find_one({"_id": ObjectId(jd_id)})
        
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )
        
        return JDResponse(
            id=str(jd["_id"]),
            job_title=jd["job_title"],
            generated_content=jd["generated_content"],
            pdf_path=jd.get("pdf_path"),
            created_at=jd["created_at"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error retrieving JD: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job description: {str(e)}"
        )

@router.get("/all")
async def get_all_jds(db = Depends(get_database)):
    """Get all job descriptions (for admin or general viewing)"""
    try:
        cursor = db["jds"].find({}).sort("created_at", -1)
        jds = await cursor.to_list(length=100)
        
        return [
            {
                "id": str(jd["_id"]),
                "job_title": jd["job_title"],
                "created_at": jd["created_at"],
                "pdf_path": jd.get("pdf_path"),
                "recruiter_id": jd.get("recruiter_id")
            }
            for jd in jds
        ]
        
    except Exception as e:
        logger.error(f"❌ Error retrieving all JDs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job descriptions: {str(e)}"
        )

@router.get("/recruiter/{recruiter_id}")
async def get_recruiter_jds(recruiter_id: str, db = Depends(get_database)):
    """Get all job descriptions created by a specific recruiter"""
    try:
        cursor = db["jds"].find({"recruiter_id": recruiter_id}).sort("created_at", -1)
        jds = await cursor.to_list(length=100)
        
        return [
            {
                "id": str(jd["_id"]),
                "job_title": jd["job_title"],
                "created_at": jd["created_at"],
                "pdf_path": jd.get("pdf_path")
            }
            for jd in jds
        ]
        
    except Exception as e:
        logger.error(f"❌ Error retrieving recruiter JDs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job descriptions: {str(e)}"
        )

