from tensorflow.keras.models import load_model
from dataclasses import dataclass
from functools import reduce
from os import listdir, path
import tensorflow as tf
import numpy as np
import time
import cv2

is_test_interactive = False

# Load the trained model
model = load_model('garage_gate_model')

# Define the labels corresponding to the model's outputs
labels = np.load('garage_gate_model/classes.npy').tolist()

@dataclass
class Test:
    is_match: bool
    filename: str
    expected_label: str
    predicted_label: str
    prediction_score: float

# Function to preprocess the image
def preprocess_image(image):
    # Resize image to 224x224
    image = cv2.resize(image, (224, 224))

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Convert the image to grayscale
    image = np.expand_dims(image, axis=-1)  # Add channel dimension
    image = (image / 255.0)  # Rescale the image array to [0, 1]
    
    # Makes the image not show able
    image = image.reshape(1, 224, 224, 1)
    
    return image

results = []

test_path = r'Dataset\Test'
files = listdir(test_path)
for filename in files:
    file_path = path.join(test_path, filename)
    expected_label = filename.split('-')[0]

    # Capture frame from the webcam
    frame = cv2.imread(file_path)
    
    # Preprocess the captured frame
    processed_frame = preprocess_image(frame)
    
    # Make prediction using the model
    predictions = model.predict(processed_frame, verbose= 0)
    predicted_label = labels[np.argmax(predictions)]
    
    test_result = Test(
        is_match= expected_label == predicted_label.replace('|', 'Or'),
        filename= filename,
        expected_label= expected_label,
        predicted_label= predicted_label,
        prediction_score=predictions[0][np.argmax(predictions)] * 100
    )
    results.append(test_result)

    if is_test_interactive:
        # Display the predicted label on the frame
        cv2.putText(frame, predicted_label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
        # Display the frame
        cv2.imshow("Garage Gate Status", frame)
    
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(1)

if is_test_interactive:
    # Release the video capture and close the windows
    cv2.destroyAllWindows()

is_pass = all(result.is_match == True for result in results)
print (f"Test result: {is_pass}")