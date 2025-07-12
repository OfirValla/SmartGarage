import signal
import sys
from typing import Optional
from camera_handler import CameraHandler
from config import validate_config

# ------------------------------------------------------------------------ #

# Handle closing the program
def signal_handler(signal: int, frame) -> None:
    print('\nYou pressed Ctrl+C!')
    if hasattr(signal_handler, 'camera_handler'):
        signal_handler.camera_handler.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ------------------------------------------------------------------------ #

def main() -> None:
    """Main function to run the LiveCollector application"""
    camera_handler: Optional[CameraHandler] = None
    
    try:
        # Validate configuration before starting
        print("Validating configuration...")
        validate_config()
        print("Configuration validated successfully")
        
        camera_handler = CameraHandler()
        signal_handler.camera_handler = camera_handler  # Store reference for signal handler
        
        print("Starting camera handler...")
        # Start consumer threads
        camera_handler.start_consumer_threads()
        print("Consumer threads started")
        
        # Process frames
        print("Starting frame processing...")
        camera_handler.process_frames()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if camera_handler is not None:
            camera_handler.cleanup()
        print("Application shutdown complete")

if __name__ == "__main__":
    main()