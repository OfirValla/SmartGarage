import logging
import numpy as np
from label_studio_ml.model import LabelStudioMLBase
from .image_io import get_image_bytes, preprocess_image
from .model_loader import (
    interpreter, input_details, output_details, inv_gate_labels, inv_parking_labels, 
    get_latest_model_dir
)

class GarageModel(LabelStudioMLBase):
    """Label Studio ML backend for garage gate and parking status prediction."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get current model version
        self.model_version = get_latest_model_dir().split('/')[-1]  # Extract V1, V2, etc.
        self.interpreter = interpreter
        self.input_details = input_details
        self.output_details = output_details
        self.inv_gate_labels = inv_gate_labels
        self.inv_parking_labels = inv_parking_labels
    
    def predict(self, tasks, **kwargs):
        results = []
        for task in tasks:
            image_url = task['data'].get('image')
            if not image_url:
                results.append({'result': []})
                continue
            try:
                image_bytes = get_image_bytes(image_url, task)
                img = preprocess_image(image_bytes)
                self.interpreter.set_tensor(self.input_details[0]['index'], img)
                self.interpreter.invoke()
                parking_pred = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                gate_pred = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
                gate_label_idx = int(np.argmax(gate_pred))
                parking_label_idx = int(np.argmax(parking_pred))
                gate_label = self.inv_gate_labels.get(gate_label_idx, str(gate_label_idx))
                parking_label = self.inv_parking_labels.get(parking_label_idx, str(parking_label_idx))
                results.append({
                    'result': [
                        {
                            'from_name': 'gate_status',
                            'to_name': 'image',
                            'type': 'choices',
                            'value': {'choices': [gate_label]}
                        },
                        {
                            'from_name': 'parking_status',
                            'to_name': 'image',
                            'type': 'choices',
                            'value': {'choices': [parking_label]}
                        }
                    ],
                    'model_version': self.model_version,
                    'meta': {
                        'model_version': self.model_version,
                        'confidence': {
                            'gate': float(np.max(gate_pred)),
                            'parking': float(np.max(parking_pred))
                        }
                    }
                })
            except Exception as e:
                logging.error(f'Prediction error for task {task.get("id")}: {e}')
                results.append({
                    'result': [],
                    'extra': {'error': str(e)},
                    'model_version': getattr(self, 'model_version', 'unknown')
                })
        return results