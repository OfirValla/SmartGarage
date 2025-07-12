import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Configuration
DISCORD_TOKEN: Optional[str] = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID: int = int(os.getenv('DISCORD_CHANNEL_ID', '0'))

# Download Configuration
NUM_DOWNLOAD_THREADS: int = int(os.getenv('NUM_DOWNLOAD_THREADS', '10'))

# MinIO Configuration
MINIO_ENDPOINT: str = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY: str = os.getenv('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY: str = os.getenv('MINIO_SECRET_KEY', 'minio_admin')
MINIO_BUCKET: str = os.getenv('MINIO_BUCKET', 'garage')
MINIO_SECURE: bool = os.getenv('MINIO_SECURE', 'false').lower() == 'true'

# Label Studio Configuration (optional)
LABEL_STUDIO_ENABLED: bool = os.getenv('LABEL_STUDIO_ENABLED', 'false').lower() == 'true'
LABEL_STUDIO_URL: str = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
LABEL_STUDIO_API_KEY: str = os.getenv('LABEL_STUDIO_API_KEY', '')
LABEL_STUDIO_PROJECT_ID: int = int(os.getenv('LABEL_STUDIO_PROJECT_ID', '0'))

def validate_config() -> None:
    """Validate required configuration"""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is required")
    if DISCORD_CHANNEL_ID == 0:
        raise ValueError("DISCORD_CHANNEL_ID environment variable is required") 