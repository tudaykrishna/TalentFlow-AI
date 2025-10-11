"""Authentication API Routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from models.user_model import (
    LoginRequest, 
    LoginResponse,
    PersistentUserCreate,
    PersistentUserResponse
)
from services.auth_service import AuthService
from db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_auth_service(db = Depends(get_database)):
    """Dependency to get auth service"""
    return AuthService(db)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with email and password
    
    - Supports both persistent users (admin/recruiter) and temporary users (candidates)
    - Automatically detects user type and role
    - Returns appropriate error messages for expired accounts or attempted interviews
    """
    try:
        user_data = await auth_service.authenticate_user(request.email, request.password)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check for specific error conditions
        if user_data.get("error") == "account_expired":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your temporary account has expired. Please contact the recruiter."
            )
        
        if user_data.get("error") == "interview_attempted":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have already completed this interview. You cannot attempt it again."
            )
        
        # Prepare response
        response = LoginResponse(
            user_id=user_data["id"],
            email=user_data["email"],
            username=user_data.get("username"),
            role=user_data["role"],
            message=f"Login successful! Welcome {user_data.get('username', 'User')}"
        )
        
        logger.info(f"✅ Login successful for {request.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/register", response_model=PersistentUserResponse, status_code=status.HTTP_201_CREATED)
async def register_persistent_user(
    request: PersistentUserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new persistent user (Admin or Recruiter)
    
    - Only for admin and recruiter roles
    - Temporary users are created automatically during interview assignment
    """
    try:
        user = await auth_service.create_persistent_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role
        )
        
        return PersistentUserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            created_at=user["created_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_user_info(
    user_id: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user information by ID (works for both persistent and temporary users)"""
    try:
        # Try persistent user first
        user = await auth_service.get_persistent_user(user_id)
        
        if not user:
            # Try temporary user
            user = await auth_service.get_temp_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user information: {str(e)}"
        )


@router.post("/cleanup-expired")
async def cleanup_expired_users(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Clean up expired temporary users
    This can be called manually or scheduled as a cron job
    """
    try:
        deleted_count = await auth_service.cleanup_expired_users()
        return {
            "message": f"Cleanup completed successfully",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup expired users: {str(e)}"
        )


@router.get("/debug/config")
async def get_backend_config():
    """
    DEBUG ENDPOINT: Show what Azure OpenAI config the backend is using
    ⚠️ WARNING: This exposes sensitive information! Only for testing!
    """
    import os
    from dotenv import load_dotenv
    
    # Reload environment to get latest values
    load_dotenv(override=True)
    
    config = {
        "azure_openai": {
            "api_key": os.getenv('AZURE_OPENAI_API_KEY', 'NOT SET'),
            "endpoint": os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET'),
            "api_version": os.getenv('AZURE_OPENAI_API_VERSION', 'NOT SET'),
            "chat_deployment": os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME', 'NOT SET'),
            "whisper_deployment": os.getenv('AZURE_OPENAI_WHISPER_DEPLOYMENT_NAME', 'NOT SET')
        },
        "mongodb": {
            "uri": os.getenv('MONGODB_URI', 'NOT SET'),
            "db_name": os.getenv('DB_NAME', 'NOT SET')
        },
        "api_settings": {
            "host": os.getenv('API_HOST', 'NOT SET'),
            "port": os.getenv('API_PORT', 'NOT SET'),
            "debug": os.getenv('DEBUG', 'NOT SET')
        }
    }
    
    # Mask API keys for security (show first 20 and last 10 chars)
    if config["azure_openai"]["api_key"] != 'NOT SET':
        key = config["azure_openai"]["api_key"]
        config["azure_openai"]["api_key_masked"] = f"{key[:20]}...{key[-10:]} ({len(key)} chars)"
        config["azure_openai"]["api_key_length"] = len(key)
        # Don't send full key in response
        del config["azure_openai"]["api_key"]
    
    # Check for issues
    issues = []
    
    if config["azure_openai"]["endpoint"] != 'NOT SET':
        if '.cognitiveservices.azure.com' in config["azure_openai"]["endpoint"]:
            issues.append("⚠️ Endpoint uses .cognitiveservices domain (OLD). Should use .openai.azure.com")
        elif '.openai.azure.com' in config["azure_openai"]["endpoint"]:
            issues.append("✅ Endpoint domain is correct (.openai.azure.com)")
    
    if config["azure_openai"]["chat_deployment"] != 'NOT SET':
        if config["azure_openai"]["chat_deployment"].startswith('"') or config["azure_openai"]["chat_deployment"].endswith('"'):
            issues.append("⚠️ Chat deployment has quotes - Azure will look for literal deployment with quotes!")
    
    config["issues_detected"] = issues
    
    return config
