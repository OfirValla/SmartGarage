import os
import json
import config

BASE_OUTPUT_PATH = config.BASE_OUTPUT_PATH

def get_latest_model_dir():
    version_dirs = [d for d in os.listdir(BASE_OUTPUT_PATH) if d.startswith('V')]
    if not version_dirs:
        raise FileNotFoundError(f'No versioned model directories found in {BASE_OUTPUT_PATH}')
    latest_version = sorted(version_dirs)[-1]
    latest_path = os.path.join(BASE_OUTPUT_PATH, latest_version)
    return latest_path, latest_version

LATEST_MODEL_DIR, LATEST_MODEL_VERSION = get_latest_model_dir()
MODEL_PATH = config.MODEL_PATH or os.path.join(LATEST_MODEL_DIR, 'garage_multi_output_model.tflite')
GATE_LABELS_PATH = config.GATE_LABELS_PATH or os.path.join(LATEST_MODEL_DIR, 'gate_labels.json')
PARKING_LABELS_PATH = config.PARKING_LABELS_PATH or os.path.join(LATEST_MODEL_DIR, 'parking_labels.json')

with open(GATE_LABELS_PATH, 'r') as f:
    gate_labels = json.load(f)
with open(PARKING_LABELS_PATH, 'r') as f:
    parking_labels = json.load(f)

inv_gate_labels = {v: k for k, v in gate_labels.items()}
inv_parking_labels = {v: k for k, v in parking_labels.items()}