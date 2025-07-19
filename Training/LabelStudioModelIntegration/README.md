# LabelStudioModelIntegration

A modular Label Studio ML backend for automated garage gate and parking status annotation using a TensorFlow Lite model. This backend supports images from HTTP(S), MinIO/S3, and local files, and is designed for easy extension and maintainability.

## Features
- Modular codebase: model loading, image IO, and backend logic are separated
- Supports HTTP(S), MinIO/S3, and local file image sources
- Uses TensorFlow Lite for fast inference
- Compatible with Label Studio's ML backend API

## Project Structure
```
LabelStudioModelIntegration/
├── garage_model/
│   ├── __init__.py         # Exports GarageModel
│   ├── model.py            # GarageModel class (Label Studio ML backend)
│   ├── image_io.py         # Image download and preprocessing
│   └── model_loader.py     # Model and label loading
├── config.py               # Loads environment variables
├── server.py               # Entrypoint for the backend
└── README.md
```

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your `.env` file (see below for variables).
3. Place your TFLite model and label maps in the appropriate output directory, or set their paths in `.env`.

## Environment Variables
Below are the variables you can set in your `.env` or `.env.example` file:

| Variable              | Required? | Description                                                      | Example/Default                |
|-----------------------|-----------|------------------------------------------------------------------|-------------------------------|
| BASE_OUTPUT_PATH      | Optional  | Directory for model version folders                               | output                        |
| MODEL_PATH            | Optional  | Path to TFLite model (auto-detects latest if not set)            |                               |
| GATE_LABELS_PATH      | Optional  | Path to gate labels JSON (auto-detects latest if not set)        |                               |
| PARKING_LABELS_PATH   | Optional  | Path to parking labels JSON (auto-detects latest if not set)     |                               |
| MINIO_ENDPOINT        | Required  | MinIO/S3 endpoint URL                                            | localhost:9000         |
| MINIO_ACCESS_KEY      | Required  | MinIO/S3 access key                                              | admin         |
| MINIO_SECRET_KEY      | Required  | MinIO/S3 secret key                                              | minio_admin         |
| MINIO_SECURE          | Optional  | Use HTTPS for MinIO connection                                   | false                         |
| LABEL_STUDIO_URL      | Optional  | Label Studio server URL (for API integration)                    | http://localhost:8080/        |
| LABEL_STUDIO_API_KEY  | Optional  | Label Studio API key (for API integration)                       |      |

**Example .env.example:**
```
# Label Studio API connection
LABEL_STUDIO_URL=http://localhost:8080/  # replace with your IP!
LABEL_STUDIO_API_KEY=label-studio-api-key

# Model and label paths (optional, will auto-detect latest if not set)
BASE_OUTPUT_PATH=output
MODEL_PATH=
GATE_LABELS_PATH=
PARKING_LABELS_PATH=

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=minio_admin
MINIO_SECURE=false
```

## Usage
- **Development:**
  ```bash
  python server.py
  ```

- The backend will be available at `http://localhost:9090/predict` (default).

## Customization
- To extend or modify the backend, edit the files in `garage_model/`.
- The main backend class is `GarageModel` in `garage_model/model.py`.

## References
- [Label Studio ML Backend Docs](https://labelstud.io/guide/ml.html)
- [MinIO Python SDK](https://github.com/minio/minio-py)

---
For questions or improvements, open an issue or PR! 