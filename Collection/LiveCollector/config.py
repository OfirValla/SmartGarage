import os
from typing import Tuple, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
CAMERA_URL: Optional[str] = os.getenv("CAMERA_URL")
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./")

# Storage Configuration
STORAGE_SYSTEM: str = os.getenv("STORAGE_SYSTEM", "local").lower()

# MinIO Configuration
MINIO_ENDPOINT: Optional[str] = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY: Optional[str] = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY: Optional[str] = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET: Optional[str] = os.getenv("MINIO_BUCKET")
MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Validate required environment variables
def validate_config() -> None:
    """Validate that required configuration is present"""
    if not CAMERA_URL:
        raise ValueError("CAMERA_URL environment variable is required. Please set it in your .env file or environment.")
    
    if not CAMERA_URL.startswith(('rtsp://', 'rtsps://', 'http://', 'https://')):
        raise ValueError("CAMERA_URL must be a valid URL starting with rtsp://, rtsps://, http://, or https://")
    
    # Validate storage system
    if STORAGE_SYSTEM not in ["local", "minio"]:
        raise ValueError("STORAGE_SYSTEM must be either 'local' or 'minio'")
    
    # Validate MinIO configuration if using MinIO storage
    if STORAGE_SYSTEM == "minio":
        if not MINIO_ENDPOINT:
            raise ValueError("MINIO_ENDPOINT is required when STORAGE_SYSTEM is 'minio'")
        if not MINIO_ACCESS_KEY:
            raise ValueError("MINIO_ACCESS_KEY is required when STORAGE_SYSTEM is 'minio'")
        if not MINIO_SECRET_KEY:
            raise ValueError("MINIO_SECRET_KEY is required when STORAGE_SYSTEM is 'minio'")
        if not MINIO_BUCKET:
            raise ValueError("MINIO_BUCKET is required when STORAGE_SYSTEM is 'minio'")

# Runtime configuration
FRAME_RATE_LIMIT: float = 1 #0.05  # seconds between frames
RUNTIME_MINUTES: int = 5
RESIZE_DIMENSIONS: Tuple[int, int] = (640, 360)
