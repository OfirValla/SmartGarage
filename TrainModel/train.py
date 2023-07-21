from sklearn.preprocessing import LabelEncoder
from os import listdir, path, mkdir
import tensorflow as tf
import numpy as np
import cv2

# ----------------------------------------------------------------------------------------------------------- #

# Split the dataset if not already splitted
if not path.exists(r'Dataset\splitted-dataset'):
    import splitfolders
    mkdir(r'Dataset\splitted-dataset')
    splitfolders.ratio(r'Dataset\dataset', output=r'Dataset\splitted-dataset', seed=1337, ratio=(.8, 0.2,0)) 

# ----------------------------------------------------------------------------------------------------------- #

# Load and preprocess the data
def preprocess_data(mode, classes_data):
    print (f'Pre-process data - {mode}')
    print (f' * Number of classes: {len(classes_data)}')
    images = []
    labels = []
    for class_data in classes_data:
        files = listdir(class_data['path'])
        
        print (f' * Class: {class_data["label"]}')
        print (f'   Detected {len(files)} files to pre-process')
        
        # Read all of the images from the path
        for filename in files:
            file_path = path.join(class_data['path'], filename)
            image = cv2.imread(file_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Convert the image to grayscale
            image = np.expand_dims(image, axis=-1)  # Add channel dimension
            image = (image / 255.0)  # Rescale the image array to [0, 1]
            
            images.append(image)
            labels.append(class_data['label'])
    
    images = np.array(images)
    
    # Perform label encoding
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    
    return images, encoded_labels, label_encoder

# ----------------------------------------------------------------------------------------------------------- #

# Define the paths to your train and test images
train_classes_dataset = [
    { 'path': r'Dataset\splitted-dataset\train\Closed', 'label': 'Closed' },
    { 'path': r'Dataset\splitted-dataset\train\Open', 'label': 'Open' },
    { 'path': r'Dataset\splitted-dataset\train\OpeningOrClosing', 'label': 'Opening|Closing' }
]
test_classes_dataset = [
    { 'path': r'Dataset\splitted-dataset\val\Closed', 'label': 'Closed' },
    { 'path': r'Dataset\splitted-dataset\val\Open', 'label': 'Open' },
    { 'path': r'Dataset\splitted-dataset\val\OpeningOrClosing', 'label': 'Opening|Closing' }
]

# ----------------------------------------------------------------------------------------------------------- #

# Load and preprocess the data
train_images, train_labels, label_encoder = preprocess_data('Train', train_classes_dataset)
Validation_images, validation_labels, _ = preprocess_data('Validation', test_classes_dataset)

# Define the model architecture
print ('Building the model')
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 1)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(label_encoder.classes_.size, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
print ('Traning the model')
model.fit(train_images, train_labels, epochs=10, validation_data=(Validation_images, validation_labels))

# Save the trained model in the TensorFlow SavedModel format and the classes from the label encoder
print('\nSaving the model')
model.save('garage_gate_model', save_format= 'tf')
np.save('garage_gate_model/classes.npy', label_encoder.classes_)