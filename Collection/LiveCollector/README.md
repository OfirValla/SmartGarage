# LiveCollector

LiveCollector is a Python application for collecting and saving images from an RTSP camera stream. It supports configurable environment variables for camera URL and output directory, and uses threading for efficient image processing. The application also supports MinIO (S3-compatible) storage for cloud-based image storage.

## Features
- Connects to an RTSP camera stream
- Saves images and grayscale versions to a specified directory
- **NEW**: MinIO/S3-compatible cloud storage support
- Uses environment variables for configuration
- Threaded consumer for image processing
- Graceful shutdown and error handling

## Requirements
- Python 3.12
- OpenCV (`cv2`)
- numpy
- python-dotenv
- minio (for cloud storage)

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a `.env` file** (see `.env.example` for reference)
4. **Run the script:**
   ```bash
   python main.py
   ```

## Environment Variables

### Camera Configuration
- `CAMERA_URL` - The RTSP URL of the camera stream

### Storage Configuration
- `STORAGE_SYSTEM` - Storage system to use: "local" or "minio" (default: "local")
- `OUTPUT_DIR` - The directory where images will be saved locally (defaults to current directory)

### MinIO Configuration (when STORAGE_SYSTEM=minio)
- `MINIO_ENDPOINT` - MinIO server endpoint (e.g., localhost:9000)
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_BUCKET` - MinIO bucket name for storing images
- `MINIO_SECURE` - Use HTTPS for MinIO connection (true/false, default: false)

## Example `.env` file
```
# Camera Configuration
CAMERA_URL=rtsp_connection_uri

# Storage Configuration
STORAGE_SYSTEM=local
OUTPUT_DIR=C:\\your\\output\\path

# MinIO Configuration (S3-compatible storage)
STORAGE_SYSTEM=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET=garage
MINIO_SECURE=false
```

## MinIO Setup

### Local MinIO Server
1. **Install MinIO:**
   ```bash
   # Download MinIO binary
   wget https://dl.min.io/server/minio/release/linux-amd64/minio
   chmod +x minio
   
   # Start MinIO server
   ./minio server /data
   ```

2. **Access MinIO Console:**
   - Open http://localhost:9000
   - Default credentials: minioadmin/minioadmin

3. **Create a bucket:**
   - Use the MinIO console or set `MINIO_BUCKET` in your `.env` file

### Cloud MinIO/S3
- Use any S3-compatible service (AWS S3, DigitalOcean Spaces, etc.)
- Set the appropriate endpoint and credentials in your `.env` file

## Storage Options

### Local Storage
Set `STORAGE_SYSTEM=local` to save images to the local filesystem.

### MinIO Storage
Set `STORAGE_SYSTEM=minio` and configure MinIO settings to save images to MinIO/S3 storage.

## License
MIT 