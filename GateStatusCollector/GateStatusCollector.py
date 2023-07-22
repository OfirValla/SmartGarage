from datetime import datetime
import numpy as np

import threading
import signal
import queue
import time
import sys
import cv2
import os 

# ------------------------------------------------------------------------ #

# Connect to the camera
buffer: queue.Queue = queue.Queue()
cap = cv2.VideoCapture("rtsps://192.168.1.1:7441/7JwpLt6hkHFBhXuy")

# ------------------------------------------------------------------------ #

# Handle closing the program
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ------------------------------------------------------------------------ #

# define the function to compute MSE between two images
def mse(img1, img2):
   h, w = img1.shape[:2]
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse, diff

# ------------------------------------------------------------------------ #

def consumer(buffer):
    counter = 0
    #last_image = None
    while True:
        # retrieve an item
        current_image = buffer.get()
        if current_image is None:
            continue
        
        # Save the image
        if not os.path.exists(f"D:/GateStatus/Collect/{datetime.now().strftime('%Y%m%d')}"):
            from pathlib import Path
            path = Path(f"D:/GateStatus/Collect/{datetime.now().strftime('%Y%m%d')}")
            path.mkdir(parents=True)
            #os.mkdir(f"D:/GateStatus/Collect/{datetime.now().strftime('%Y%m%d')}")
            counter = 0

        cv2.imwrite(f"D:/GateStatus/Collect/{datetime.now().strftime('%Y%m%d')}/{counter}.jpg", current_image)
        image_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"D:/GateStatus/Collect/{datetime.now().strftime('%Y%m%d')}/{counter}-Gray.jpg", image_gray)
        counter += 1
        
# ------------------------------------------------------------------------ #

consumer_threads: list[threading.Thread] = []
consumer_threads.append(threading.Thread(target=consumer, args=(buffer,)))

for thread in consumer_threads:
    thread.start()

start_time = time.time()
last_time = time.time()

cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
while(cap.isOpened()):
    _, frame = cap.read()
    
    # Skip empty frames
    if frame is None:
        continue

    # Check if one second has passed
    curr_time = time.time()
    if curr_time - last_time < .05:
        continue

    # The script will run for X amount of minutes
    if curr_time - start_time > 60 * 5:
        print ("Shutdown")
        break
    last_time = curr_time
    
    # Crop the image to contain only the gate part
    (h, w) = frame.shape[:2]
    cropped_image = frame[:h - 225, 200:w - 150] 
    cropped_image = cv2.resize(cropped_image, (224, 224), interpolation=cv2.INTER_AREA)
    buffer.put(cropped_image)
    
    cv2.imshow('frame', frame)
    cv2.imshow('cropped', cropped_image)
    
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break


for thread in consumer_threads:
    thread.join()

cv2.destroyAllWindows()