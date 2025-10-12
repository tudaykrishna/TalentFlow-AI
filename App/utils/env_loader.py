"""Utility to load .env file from correct location"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env_from_root():
    """Load .env file from project root directory"""
    # Get the project root (2 levels up from this file)
    current_file = Path(__file__).resolve()
    app_dir = current_file.parent.parent  # App directory
    project_root = app_dir.parent  # Project root
    
    # Path to .env file
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path, override=True)
        return True
    else:
        # Try loading from current directory as fallback
        load_dotenv(override=True)
        return False

# Load immediately when module is imported
load_env_from_root()

