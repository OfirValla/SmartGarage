import os
from typing import Tuple, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
CAMERA_URL: Optional[str] = os.getenv("CAMERA_URL")
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")

# Validate required environment variables
def validate_config() -> None:
    """Validate that required configuration is present"""
    if not CAMERA_URL:
        raise ValueError("CAMERA_URL environment variable is required. Please set it in your .env file or environment.")
    
    if not CAMERA_URL.startswith(('rtsp://', 'rtsps://', 'http://', 'https://')):
        raise ValueError("CAMERA_URL must be a valid URL starting with rtsp://, rtsps://, http://, or https://")

# Runtime configuration
FRAME_RATE_LIMIT: float = 1 #0.05  # seconds between frames
RUNTIME_MINUTES: int = 5
RESIZE_DIMENSIONS: Tuple[int, int] = (640, 360)
