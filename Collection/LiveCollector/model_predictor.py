import os
import cv2
import numpy as np
from typing import Optional, Tuple
import tensorflow as tf
from pathlib import Path

class ModelPredictor:
    def __init__(self, model_path: str = "../../models/Old Garage Model") -> None:
        """Initialize the model predictor"""
        self.model_path = Path(model_path)
        self.model: Optional[tf.keras.Model] = None
        self.labels: list = []
        self.load_model()
    
    def load_model(self) -> None:
        """Load the model from the specified path"""
        try:
            if not self.model_path.exists():
                print(f"Model path does not exist: {self.model_path}")
                return
            
            # Try to load the model
            if (self.model_path / "model.h5").exists():
                self.model = tf.keras.models.load_model(str(self.model_path / "model.h5"))
                print(f"Loaded model from: {self.model_path / 'model.h5'}")
            elif (self.model_path / "saved_model.pb").exists():
                self.model = tf.keras.models.load_model(str(self.model_path))
                print(f"Loaded model from: {self.model_path}")
            else:
                # Try to load any .h5 or .pb file in the directory
                model_files = list(self.model_path.glob("*.h5")) + list(self.model_path.glob("*.pb"))
                if model_files:
                    self.model = tf.keras.models.load_model(str(model_files[0]))
                    print(f"Loaded model from: {model_files[0]}")
                else:
                    print(f"No model files found in: {self.model_path}")
                    return
            
            # Load labels from classes.npy
            classes_file = self.model_path / "classes.npy"
            if classes_file.exists():
                self.labels = np.load(str(classes_file)).tolist()
                print(f"Loaded labels from classes.npy: {self.labels}")
            else:
                # Default labels for gate status
                self.labels = ["Closed", "Open"]
                print("Using default labels: Closed, Open")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess frame for model input using the exact method from training"""
        try:
            # Crop image
            (h, w) = frame.shape[:2]
            image = frame[:h - 225, 200:w - 150] 

            # Resize image to 224x224
            resized_image = cv2.resize(image, (224, 224))

            # Convert BGR to RGB
            image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            
            # Convert the image to grayscale
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Add channel dimension
            image = np.expand_dims(image, axis=-1)
            
            # Rescale the image array to [0, 1]
            image = (image / 255.0)
        
            # Reshape for model input (batch, height, width, channels)
            image = image.reshape(1, 224, 224, 1)
        
            return image, resized_image
            
        except Exception as e:
            print(f"Error preprocessing frame: {e}")
            return None, None
    
    def predict(self, frame: np.ndarray) -> Tuple[str, float]:
        """Make prediction on a frame"""
        if self.model is None:
            return "Model not loaded", 0.0
        
        try:
            # Preprocess the frame
            processed_frame, resized_image = self.preprocess_frame(frame)
            if processed_frame is None:
                return "Preprocessing failed", 0.0
            
            # Make prediction
            predictions = self.model.predict(processed_frame, verbose=0)
            
            # Get the predicted class and confidence
            predicted_class = np.argmax(predictions[0])
            confidence = float(np.max(predictions[0]))
            
            # Get the label
            if predicted_class < len(self.labels):
                label = self.labels[predicted_class]
            else:
                label = f"Class {predicted_class}"
            
            return label, confidence
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            return "Prediction failed", 0.0
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded successfully"""
        return self.model is not None 