import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080/')
LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY', '')
LABEL_STUDIO_PROJECT_ID = os.getenv('LABEL_STUDIO_PROJECT_ID', '')

# Model and label paths (used by my_model.py)
BASE_OUTPUT_PATH = os.getenv('BASE_OUTPUT_PATH', 'output')
MODEL_PATH = os.getenv('MODEL_PATH')
GATE_LABELS_PATH = os.getenv('GATE_LABELS_PATH')
PARKING_LABELS_PATH = os.getenv('PARKING_LABELS_PATH') 

# MinIO credentials
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')  # For MinIO, e.g. http://localhost:9000
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minio_admin')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'