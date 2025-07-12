# LiveCollector

LiveCollector is a Python application for collecting and saving images from an RTSP camera stream. It supports configurable environment variables for camera URL and output directory, and uses threading for efficient image processing.

## Features
- Connects to an RTSP camera stream
- Saves images and grayscale versions to a specified directory
- Uses environment variables for configuration
- Threaded consumer for image processing

## Requirements
- Python 3.12
- OpenCV (`cv2`)
- numpy
- python-dotenv

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
The application uses the following environment variables (set in your `.env` file):

Required environment variables: 
- `CAMERA_URL` - The RTSP URL of the camera stream

Optional environment variables:
- `OUTPUT_DIR` - The directory where images will be saved (default: ./output)

## Example `.env` file
See `.env.example` in the repository for a template.

## License
MIT 