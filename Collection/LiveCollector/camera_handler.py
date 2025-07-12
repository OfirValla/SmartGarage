import cv2
import queue
import threading
import time
from typing import List
import numpy as np
from config import CAMERA_URL, FRAME_RATE_LIMIT, RUNTIME_MINUTES, RESIZE_DIMENSIONS
from image_consumer import consumer

class CameraHandler:
    def __init__(self) -> None:
        self.buffer: queue.Queue = queue.Queue()
        # CAMERA_URL is validated in config.py, so it should not be None here
        if CAMERA_URL is None:
            raise ValueError("CAMERA_URL is None - this should not happen after validation")
        self.cap: cv2.VideoCapture = cv2.VideoCapture(CAMERA_URL)
        self.consumer_threads: List[threading.Thread] = []
        
    def start_consumer_threads(self) -> None:
        """Start the consumer threads"""
        self.consumer_threads.append(threading.Thread(target=consumer, args=(self.buffer,)))
        
        for thread in self.consumer_threads:
            thread.start()
    
    def process_frames(self) -> None:
        """Main frame processing loop"""
        start_time: float = time.time()
        last_time: float = time.time()
        
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        
        while self.cap.isOpened():
            ret: bool
            frame: np.ndarray | None
            ret, frame = self.cap.read()
            
            # Skip empty frames
            if frame is None:
                continue

            # Check if enough time has passed since last frame
            curr_time: float = time.time()
            if curr_time - last_time < FRAME_RATE_LIMIT:
                continue

            # Check if runtime limit has been reached
            if curr_time - start_time > 60 * RUNTIME_MINUTES:
                print("Shutdown")
                break
            last_time = curr_time
            
            # Crop and resize the image
            resized_image: np.ndarray = cv2.resize(frame, RESIZE_DIMENSIONS, interpolation=cv2.INTER_AREA)
            self.buffer.put(resized_image)
            
            cv2.imshow('frame', resized_image)
            
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
    
    def cleanup(self) -> None:
        """Clean up resources"""
        for thread in self.consumer_threads:
            thread.join()
        
        self.cap.release()
        cv2.destroyAllWindows() 