# LiveModelValidation

A standalone project for real-time validation of the garage gate model using a camera feed and a TensorFlow Lite model.

## Features
- Loads the latest TFLite model and label maps from the output directory
- Connects to a camera via RTSP
- Processes frames in real-time at a configurable FPS
- Displays predictions and (optionally) saves frames when the predicted label changes

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy your TFLite model and label maps (gate_labels.json, parking_labels.json) to an `output/V*` directory.
3. Configure your `.env` file (see `.env.example`).
4. Run live validation:
   ```bash
   python main.py live
   ```

## Configuration

All configuration is handled via environment variables. See `.env.example` for all options.

- `CAMERA_RTSP_URL`: RTSP URL for your camera
- `LIVE_TEST_FPS`: Frames per second for live testing
- `LIVE_TEST_SAVE_IMAGES`: Whether to save images when predictions change
- `LIVE_TEST_PREDICTIONS_DIR`: Directory to save prediction images

## File Structure
```
LiveModelValidation/
├── main.py
├── live_test.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements
- Python 3.7+
- TensorFlow
- OpenCV
- NumPy
- python-dotenv

## Notes
- This project is standalone and does not require the training code.
- Ensure your TFLite model and label maps are present in the expected output directory structure. 