import os
import io
from datetime import datetime
from typing import Optional
from minio import Minio
from minio.error import S3Error
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, MINIO_SECURE

class MinioManager:
    def __init__(self) -> None:
        self.client: Minio = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure MinIO bucket exists"""
        try:
            if not self.client.bucket_exists(MINIO_BUCKET):
                self.client.make_bucket(MINIO_BUCKET)
                print(f"[{datetime.now()}] INFO: Created MinIO bucket '{MINIO_BUCKET}'")
            else:
                print(f"[{datetime.now()}] INFO: MinIO bucket '{MINIO_BUCKET}' already exists")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Failed to connect to MinIO: {e}")
    
    def upload_file(self, file_data: bytes, filename: str, content_type: Optional[str] = None) -> bool:
        """Upload file data to MinIO"""
        try:
            # Create a BytesIO object for MinIO upload
            file_stream = io.BytesIO(file_data)
            file_stream.seek(0)
            
            # Determine content type if not provided
            if not content_type:
                _, ext = os.path.splitext(filename)
                content_type = self._get_content_type(ext)
            
            # Upload to MinIO
            self.client.put_object(
                MINIO_BUCKET,
                filename,
                file_stream,
                length=len(file_data),
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"[{datetime.now()}] ERROR: Failed to upload {filename} to MinIO: {e}")
            return False
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Failed to upload {filename} to MinIO: {e}")
            return False
    
    def _get_content_type(self, ext: str) -> str:
        """Get content type based on file extension"""
        ext = ext.lower()
        if ext in ['.jpg', '.jpeg']:
            return "image/jpeg"
        elif ext == '.png':
            return "image/png"
        elif ext == '.gif':
            return "image/gif"
        else:
            return "application/octet-stream"
    
    def get_file_url(self, filename: str) -> str:
        """Get the URL for a file in MinIO"""
        return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{filename}" 