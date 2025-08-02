import cv2
import os
from datetime import datetime
from pathlib import Path
import queue
import threading
import time
from config import OUTPUT_DIR, STORAGE_SYSTEM
from minio_storage import MinIOStorage

def consumer(buffer: queue.Queue, stop_flag: threading.Event) -> None:
    """Consumer thread that saves images based on the configured storage system"""
    minio_storage: MinIOStorage | None = None
    
    if STORAGE_SYSTEM == "none":
        print("Storage system is set to none, no images will be saved")
        return

    # Initialize MinIO storage if using MinIO
    if STORAGE_SYSTEM == "minio":
        try:
            minio_storage = MinIOStorage()
            print("MinIO storage initialized")
        except Exception as e:
            print(f"Failed to initialize MinIO storage: {e}")
            minio_storage = None
    
    while not stop_flag.is_set():
        try:
            # retrieve an item with timeout to allow checking stop_flag
            current_image = buffer.get(timeout=1.0)
            if current_image is None:
                continue
            
            # Generate filename using epoch time
            epoch_time = int(time.time())
            filename = f"{epoch_time}.jpg"
            
            # Create output directory if using local storage
            if STORAGE_SYSTEM == "local":
                local_date_str: str = datetime.now().strftime('%Y%m%d')
                output_path: str = os.path.join(OUTPUT_DIR, local_date_str)
                
                if not os.path.exists(output_path):
                    path = Path(output_path)
                    path.mkdir(parents=True)

                # Save to local file system
                image_filename = os.path.join(output_path, filename)
                cv2.imwrite(image_filename, current_image)
                
                print(f"Saved locally: {image_filename}")
            
            # Upload to MinIO if using MinIO storage
            elif STORAGE_SYSTEM == "minio" and minio_storage is not None:
                try:
                    # Upload original image
                    if minio_storage.upload_cv2_image(current_image, filename):
                        print(f"Uploaded to MinIO: {filename}")
                        
                except Exception as e:
                    print(f"Failed to upload to MinIO: {e}")
            
        except queue.Empty:
            # Timeout occurred, check stop_flag and continue
            continue
        except Exception as e:
            print(f"Error in consumer thread: {e}")
            continue
    
    print("Consumer thread stopped") 