import io
import cv2
from datetime import datetime
from typing import Optional
from minio import Minio
from minio.error import S3Error
from config import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, 
    MINIO_BUCKET, MINIO_SECURE, STORAGE_SYSTEM
)

class MinIOStorage:
    def __init__(self) -> None:
        """Initialize MinIO client"""
        if STORAGE_SYSTEM != "minio":
            raise ValueError("MinIO storage is not enabled. Set STORAGE_SYSTEM=minio to enable.")
        
        if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET]):
            raise ValueError("MinIO configuration is incomplete")
        
        # Type checking to ensure values are not None
        if MINIO_ENDPOINT is None or MINIO_ACCESS_KEY is None or MINIO_SECRET_KEY is None or MINIO_BUCKET is None:
            raise ValueError("MinIO configuration values cannot be None")
        
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self.bucket = MINIO_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"Created bucket: {self.bucket}")
            else:
                print(f"Using existing bucket: {self.bucket}")
        except S3Error as e:
            raise ValueError(f"Failed to create/access bucket {self.bucket}: {e}")
    
    def upload_image(self, image: bytes, filename: str, content_type: str = "image/jpeg") -> bool:
        """Upload an image to MinIO"""
        try:
            image_data = io.BytesIO(image)
            self.client.put_object(
                self.bucket,
                filename,
                image_data,
                length=len(image),
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Failed to upload {filename}: {e}")
            return False
    
    def upload_cv2_image(self, image, filename: str) -> bool:
        """Upload a cv2 image to MinIO"""
        try:
            # Encode image to JPEG format
            success, encoded_image = cv2.imencode('.jpg', image)
            if not success:
                print(f"Failed to encode image: {filename}")
                return False
            
            # Convert to bytes
            image_bytes = encoded_image.tobytes()
            
            # Upload to MinIO
            return self.upload_image(image_bytes, filename)
            
        except Exception as e:
            print(f"Error uploading cv2 image {filename}: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test MinIO connection"""
        try:
            # Try to list buckets to test connection
            self.client.list_buckets()
            print("MinIO connection successful")
            return True
        except Exception as e:
            print(f"MinIO connection failed: {e}")
            return False 