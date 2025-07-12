import cv2
import os
from datetime import datetime
from pathlib import Path
import queue
import threading
from config import OUTPUT_DIR

def consumer(buffer: queue.Queue, stop_flag: threading.Event) -> None:
    """Consumer thread that saves images from the buffer to disk"""
    counter: int = 0
    
    while not stop_flag.is_set():
        try:
            # retrieve an item with timeout to allow checking stop_flag
            current_image = buffer.get(timeout=1.0)
            if current_image is None:
                continue
            
            # Create output directory if it doesn't exist
            date_str: str = datetime.now().strftime('%Y%m%d')
            output_path: str = os.path.join(OUTPUT_DIR, date_str)
            
            if not os.path.exists(output_path):
                path = Path(output_path)
                path.mkdir(parents=True)
                counter = 0

            # Save the original image
            image_filename = os.path.join(output_path, f"{counter}.jpg")
            cv2.imwrite(image_filename, current_image)
            
            # Save grayscale version
            #image_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
            #gray_filename = os.path.join(output_path, f"{counter}-Gray.jpg")
            #cv2.imwrite(gray_filename, image_gray)
            
            counter += 1
            
        except queue.Empty:
            # Timeout occurred, check stop_flag and continue
            continue
        except Exception as e:
            print(f"Error in consumer thread: {e}")
            continue
    
    print("Consumer thread stopped") 