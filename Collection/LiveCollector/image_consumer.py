import cv2
import os
from datetime import datetime
from pathlib import Path
from typing import NoReturn
import queue
from config import OUTPUT_DIR

def consumer(buffer: queue.Queue) -> NoReturn:
    """Consumer thread that saves images from the buffer to disk"""
    counter: int = 0
    
    while True:
        # retrieve an item
        current_image = buffer.get()
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
        # image_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
        # cv2.imwrite(f"{output_path}/{counter}-Gray.jpg", image_gray)
        
        counter += 1 