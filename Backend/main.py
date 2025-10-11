"""
TalentFlow AI - FastAPI Backend
HR Recruiter Application Backend
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
# Get the directory containing this file (Backend/)
backend_dir = Path(__file__).parent
# Go up one level to project root
project_root = backend_dir.parent
env_path = project_root / '.env'

# Load .env file
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger(__name__)
logger.info(f"Loading .env from: {env_path}")
logger.info(f".env file exists: {env_path.exists()}")

# Import database (after loading .env)
from db.mongodb import mongodb

# Configure logging BEFORE importing routes (so services can log during init)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import routes (after logging is configured)
from routes.auth_routes import router as auth_router
from routes.jd_routes import router as jd_router
from routes.resume_routes import router as resume_router
from routes.interview_routes import router as interview_router

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("🚀 Starting TalentFlow AI Backend...")
    try:
        await mongodb.connect()
        logger.info("✅ Application started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down TalentFlow AI Backend...")
    await mongodb.close()
    logger.info("✅ Application shut down successfully")

# Create FastAPI app
app = FastAPI(
    title="TalentFlow AI",
    description="AI-Powered HR Recruiter Application Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving PDFs and uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(jd_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(interview_router, prefix="/api")

# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TalentFlow AI Backend",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "authentication": "/api/auth",
            "job_descriptions": "/api/jd",
            "resume_screening": "/api/resume",
            "ai_interviews": "/api/interview",
            "documentation": "/docs"
        }
    }

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    try:
        # Try to ping the database to test connection
        if mongodb.client is not None:
            await mongodb.client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
            
        return {
            "status": "healthy",
            "database": db_status
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "healthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
