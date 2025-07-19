import requests
import cv2
import numpy as np
import logging
from urllib.parse import urlparse
from minio import Minio
import config

def get_image_bytes(image_url, task):
    """Download image as bytes from HTTP, S3/MinIO, or local file."""
    if image_url.startswith('http://') or image_url.startswith('https://'):
        resp = requests.get(image_url)
        resp.raise_for_status()
        return resp.content
    elif image_url.startswith('s3://'):
        endpoint_url = config.MINIO_ENDPOINT
        access_key = config.MINIO_ACCESS_KEY
        secret_key = config.MINIO_SECRET_KEY
        secure = config.MINIO_SECURE
        if not endpoint_url or not access_key or not secret_key:
            raise ValueError('MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY must be set for MinIO access')
        parsed = urlparse(image_url)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        try:
            minio_client = Minio(
                endpoint_url.replace('http://', '').replace('https://', ''),
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            response = minio_client.get_object(bucket, key)
            data = response.data
            response.close()
            response.release_conn()
            return data
        except Exception as minio_err:
            logging.error(f'Minio error: endpoint={endpoint_url}, secure={secure}, bucket={bucket}, key={key}, error={minio_err}')
            raise
    elif image_url.startswith('file://'):
        local_path = image_url[7:]
        with open(local_path, 'rb') as f:
            return f.read()
    else:
        # Assume local path
        with open(image_url, 'rb') as f:
            return f.read()

def preprocess_image(image_bytes):
    """Convert image bytes to preprocessed numpy array for model input."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (360, 640))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    return img 