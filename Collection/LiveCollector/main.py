import signal
import sys
from camera_handler import CameraHandler
from config import validate_config

# ------------------------------------------------------------------------ #

# Handle closing the program
def signal_handler(signal: int, frame) -> None:
    print('You pressed Ctrl+C!')
    if hasattr(signal_handler, 'camera_handler'):
        signal_handler.camera_handler.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ------------------------------------------------------------------------ #

def main() -> None:
    """Main function to run the LiveCollector application"""
    try:
        # Validate configuration before starting
        validate_config()
        
        camera_handler: CameraHandler = CameraHandler()
        signal_handler.camera_handler = camera_handler  # Store reference for signal handler
        
        # Start consumer threads
        camera_handler.start_consumer_threads()
        
        # Process frames
        camera_handler.process_frames()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        if 'camera_handler' in locals():
            camera_handler.cleanup()

if __name__ == "__main__":
    main()