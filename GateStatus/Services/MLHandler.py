from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

import numpy as np
import cv2
import gc

# --------------------------------------------------------------------------------------------------- #

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# --------------------------------------------------------------------------------------------------- #

class MLHandler():
    def __init__(self, max_usage_per_load = 1000, verbose = False):
        self._model_path = "garage_gate_model"
        self._max_usage_per_load = max_usage_per_load
        self._verbose = verbose
        
        self.__load()
       
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
    
    def preprocess_image(self, image):
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
   