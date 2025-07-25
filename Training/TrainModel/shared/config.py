import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model configuration
model_path = os.getenv('MODEL_PATH', 'garage_gate_model')
model_epochs = int(os.getenv('MODEL_EPOCHS', 10))
model_seed = int(os.getenv('MODEL_SEED', 1337))
train_validation_ratio = tuple(map(float, os.getenv('TRAIN_VALIDATION_RATIO', '0.8,0.2,0').split(',')))

# Camera configuration
camera_rtsp_url = os.getenv('CAMERA_RTSP_URL', 'RTSP_URL')
camera_width = int(os.getenv('CAMERA_WIDTH', 640))
camera_height = int(os.getenv('CAMERA_HEIGHT', 480))
camera_refresh_interval = int(os.getenv('CAMERA_REFRESH_INTERVAL', 100))

# Logging configuration
log_level = os.getenv('LOG_LEVEL', 'INFO')

label_studio_url = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
label_studio_api_key = os.getenv('LABEL_STUDIO_API_KEY', '')
label_studio_project_id = int(os.getenv('LABEL_STUDIO_PROJECT_ID', 1)) 