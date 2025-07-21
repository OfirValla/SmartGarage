import requests
import tensorflow as tf
from shared.label_studio_utils import LabelStudioManager
from shared.task_statistics import TaskStatistics
from shared import config

IMAGE_SIZE = (640, 360)
BATCH_SIZE = 16

def get_task_statistics(ls_manager, gate_label_map, parking_label_map):
    """Get statistics about tasks, including label choice counts."""
    total_tasks = 0
    gate_status_counts = {label: 0 for label in gate_label_map.keys()}
    parking_status_counts = {label: 0 for label in parking_label_map.keys()}

    for task in ls_manager.fetch_annotated_tasks():
        total_tasks += 1
        if not task.get('is_labeled'):
            continue
        
        annotations = task['annotations'][0]['result'] if task['annotations'] and task['annotations'][0].get('result') else []
        gate_status = None
        parking_status = None
        
        for ann in annotations:
            if ann.get('to_name') == 'image':
                if ann.get('from_name') == 'gate_status':
                    gate_status = ann['value']['choices'][0]
                elif ann.get('from_name') == 'parking_status':
                    parking_status = ann['value']['choices'][0]
        if gate_status in gate_status_counts:
            gate_status_counts[gate_status] += 1
        if parking_status in parking_status_counts:
            parking_status_counts[parking_status] += 1
    return TaskStatistics(total_tasks, gate_status_counts=gate_status_counts, parking_status_counts=parking_status_counts)

def task_label_generator(ls_manager, gate_label_map, parking_label_map):
    """Generator that yields (url, gate_label, parking_label) for each valid annotated task."""
    for task in ls_manager.fetch_annotated_tasks():
        if not task.get('is_labeled'):
            continue

        img_url = task['data'].get('image')
        annotations = task['annotations'][0]['result'] if task['annotations'] and task['annotations'][0].get('result') else []
        
        gate_status = None
        parking_status = None
        
        for ann in annotations:
            if ann.get('to_name') == 'image':
                if ann.get('from_name') == 'gate_status':
                    gate_status = ann['value']['choices'][0]
                elif ann.get('from_name') == 'parking_status':
                    parking_status = ann['value']['choices'][0]
        
        if img_url and gate_status and parking_status:
            yield img_url, gate_label_map.get(gate_status), parking_label_map.get(parking_status)

def fetch_image_py(url):
    """Fetch and preprocess image from URL."""
    url = url.numpy().decode('utf-8')
    headers = {'Authorization': f'Token {config.label_studio_api_key}'}

    if url.startswith('/'):
        url = config.label_studio_url.rstrip('/') + url
    
    print(f"Fetching image from URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Bad HTTP response: {response.status_code} for URL {url}")
    
    img = tf.io.decode_image(response.content, channels=3, expand_animations=False)
    img = tf.image.resize(img, IMAGE_SIZE)
    img = tf.cast(img, tf.float32) / 255.0  # Ensure float32 dtype
    return img

def load_image(url, gate_label, parking_label):
    """Load and preprocess image with labels."""
    img = tf.py_function(fetch_image_py, [url], tf.float32)
    img.set_shape((640, 360, 3))
    return img, {'gate_output': gate_label, 'parking_output': parking_label}

def create_dataset(ls_manager, gate_label_map, parking_label_map):
    """Create TensorFlow dataset from Label Studio data."""
    dataset = tf.data.Dataset.from_generator(
        lambda: task_label_generator(ls_manager, gate_label_map, parking_label_map),
        output_signature=(
            tf.TensorSpec(shape=(), dtype=tf.string),   # URL
            tf.TensorSpec(shape=(), dtype=tf.int32),    # gate label
            tf.TensorSpec(shape=(), dtype=tf.int32)     # parking label
        )
    )

    dataset = dataset.shuffle(buffer_size=1000)
    dataset = dataset.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    
    return dataset

def split_dataset(dataset, num_samples, train_split=0.8):
    """Split dataset into training and validation sets."""
    train_size = int(train_split * num_samples)
    dataset = dataset.shuffle(buffer_size=min(1000, num_samples), reshuffle_each_iteration=True)
    train_dataset = dataset.take(train_size).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    val_dataset = dataset.skip(train_size).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    
    return train_dataset, val_dataset
