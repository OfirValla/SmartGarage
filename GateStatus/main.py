from dataclasses import dataclass
import DiscordSender

from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

from colorama import Fore, Style
from datetime import datetime

import cv2  # Install opencv-python
import numpy as np
import time
import gc
import os 

# --------------------------------------------------------------------------------------------------- #

CAMERA_RTSP = os.getenv('RTSP_URL')

# --------------------------------------------------------------------------------------------------- #

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# --------------------------------------------------------------------------------------------------- #

class CameraHandler():
    def __init__(self, verbose = False):
        print ("Init camera manager")
        self.video_capture = None
        self.call_counter = 0
        self._verbose = verbose

    def camera(self, reset = False):
        self.call_counter += 1
        if self.call_counter == 100 or reset:
            if self._verbose:
                print("Refreshing camera connection")
                print(" * Closing connection")
            self.call_counter = 0
            
            self.video_capture.release()
            self.video_capture = None

        if self.video_capture is None:
            if self._verbose:
                print(f" * {Fore.LIGHTGREEN_EX}Connecting to camera{Style.RESET_ALL}")
            self.video_capture = cv2.VideoCapture(CAMERA_RTSP, apiPreference=cv2.CAP_FFMPEG)

        return self.video_capture

# --------------------------------------------------------------------------------------------------- #

class MLHandler():
    def __init__(self, max_usage_per_load = 1000, verbose = False):
        self._model_path = "garage_gate_model"
        self._max_usage_per_load = max_usage_per_load
        self._verbose = verbose
        
        self.__load()

        self._model.summary()

    def __load(self):
        from os import path

        if self._verbose:
            print ("Loading")

        self._model_usage_counter = 0 # Reset usage counter
        self._model = load_model(self._model_path, compile=False) # Load the model
        self._class_names = np.load(path.join(self._model_path, "classes.npy")).tolist() # Load the labels

    def __unload(self):
        if self._verbose:
            print("Unloading")

        del self._model
        gc.collect()
        K.clear_session()
        
    def predict(self, input_data):
        self._model_usage_counter += 1
        
        # Reload the model
        if self._model_usage_counter == self._max_usage_per_load:
            self.__unload()
            self.__load()

        prediction = self._model(input_data)
        index = np.argmax(prediction)
        class_name = self._class_names[index]
        confidence_score = prediction[0][index]

        return (class_name, np.round(confidence_score * 100))
    
# --------------------------------------------------------------------------------------------------- #

def preprocess_image(image):
    # Crop image
    (h, w) = image.shape[:2]
    image = image[:h - 225, 200:w - 150] 

    # Resize image to 224x224
    image = resized_image = cv2.resize(image, (224, 224))

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Convert the image to grayscale
    image = np.expand_dims(image, axis=-1)  # Add channel dimension
    image = (image / 255.0)  # Rescale the image array to [0, 1]
    
    # Makes the image not showable
    image = image.reshape(1, 224, 224, 1)
    
    return image, resized_image

# --------------------------------------------------------------------------------------------------- #

def main():
    camera_manager = CameraHandler()
    model = MLHandler()
    last_status = ""
    last_time = time.time()
    print("Starting")

    while True:
        success, frame = camera_manager.camera().read()
        
        if not success:
            camera_manager.camera(reset= True)
        
        # Skip empty frames
        if frame is None:
            continue

        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break

        curr_time = time.time()

        original_frame = frame
        
        frame, _ = preprocess_image(frame)
        
        if curr_time - last_time < .5:
            continue
        last_time = curr_time
        
        class_name, confidence_score = model.predict(frame)

        # On prediction change send alert to discord
        if last_status != class_name:
            last_status = class_name
            print(datetime.now())
            print(f"Class: {class_name}")
            print(f"Confidence Score: {str(confidence_score)[:-2]}%")
            DiscordSender.send_discord_message(class_name, str(confidence_score)[:-2], cv2.imencode('.jpg', original_frame)[1])
            
# --------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()