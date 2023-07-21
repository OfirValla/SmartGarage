from tensorflow.keras.models import load_model
from tabnanny import verbose
from os import path, mkdir
import tensorflow as tf
import numpy as np
import cv2

# ----------------------------------------------------------------------------------------------------------- #

# Load the trained model
model = load_model('garage_gate_model')

# Define the labels corresponding to the model's outputs
labels = np.load('garage_gate_model/classes.npy').tolist()

# Set up the video capture
CAMERA_RTSP = 'RTSP_URL'

# ----------------------------------------------------------------------------------------------------------- #

class CameraHandler():
    def __init__(self, verbose = False):
        print ('Init camera manager')
        self.video_capture = None
        self.call_counter = 0
        self._verbose = verbose

    def camera(self, reset = False):
        self.call_counter += 1
        if self.call_counter == 100 or reset:
            if self._verbose:
                print('Refreshing camera connection')
                print(' * Closing connection')
            self.call_counter = 0
            
            self.video_capture.release()
            self.video_capture = None

        if self.video_capture is None:
            if self._verbose:
                print(f' * Connecting to camera')
            self.video_capture = cv2.VideoCapture(CAMERA_RTSP, apiPreference=cv2.CAP_FFMPEG)
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        return self.video_capture

# ----------------------------------------------------------------------------------------------------------- #

# Function to preprocess the image
def preprocess_image(image):
    # Crop image
    (h, w) = image.shape[:2]
    image = image[:h - 225, 200:w - 150] 

    # Resize image to 224x224
    image = cv2.resize(image, (224, 224))

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Convert the image to grayscale
    image = np.expand_dims(image, axis=-1)  # Add channel dimension
    image = (image / 255.0)  # Rescale the image array to [0, 1]
    
    # Makes the image not showable
    image = image.reshape(1, 224, 224, 1)
    
    return image

# ----------------------------------------------------------------------------------------------------------- #

mkdir(r'LiveTest\Predictions', exist_ok=True)

cap = CameraHandler()
last_label = ''
counter = 0

while True:
    # Capture frame from the webcam
    ret, frame = cap.camera().read()
    
    if frame is None:
        continue

    # Preprocess the captured frame
    processed_frame = preprocess_image(frame)
    
    # Make prediction using the model
    predictions = model.predict(processed_frame, verbose= 0)
    predicted_label = labels[np.argmax(predictions)]
    
    if last_label != predicted_label:
        last_label = predicted_label
        counter += 1
        print (f'Prediction: {predicted_label} ( {predictions[0][np.argmax(predictions)] * 100}% )')
        cv2.imwrite(f'LiveTest/Predictions/{counter} - {last_label}.jpg', frame)

    # Display the predicted label on the frame
    cv2.putText(frame, f'{predicted_label} ( {predictions[0][np.argmax(predictions)] * 100}% )', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Display the frame
    cv2.imshow('Garage Gate Status', frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()