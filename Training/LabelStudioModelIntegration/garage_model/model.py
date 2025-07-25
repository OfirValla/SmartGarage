import config
import logging
import numpy as np
import tensorflow as tf
from label_studio_ml.model import LabelStudioMLBase
from label_studio_sdk import Client
from .image_io import get_image_bytes, preprocess_image
from .model_loader import (
    inv_gate_labels, inv_parking_labels, 
    LATEST_MODEL_VERSION, MODEL_PATH
)

class GarageModel(LabelStudioMLBase):
    """Label Studio ML backend for garage gate and parking status prediction."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ls = Client(url=config.LABEL_STUDIO_URL, api_key=config.LABEL_STUDIO_API_KEY)
        self.project = self.ls.get_project(config.LABEL_STUDIO_PROJECT_ID)

        self.model_version = LATEST_MODEL_VERSION

        # ✅ Each instance gets its own interpreter
        self.interpreter = tf.lite.Interpreter(
            model_path=MODEL_PATH,
            # experimental_delegates=[
            #     tf.lite.experimental.load_delegate('libtensorflowlite_gpu_delegate.so')
            # ]
        )
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

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

                parking_pred_tensor = self.interpreter.get_tensor(self.output_details[0]['index']).copy()
                gate_pred_tensor = self.interpreter.get_tensor(self.output_details[1]['index']).copy()

                parking_pred = parking_pred_tensor[0]
                gate_pred = gate_pred_tensor[0]
                gate_label_idx = int(np.argmax(gate_pred))
                parking_label_idx = int(np.argmax(parking_pred))
                gate_label = self.inv_gate_labels.get(gate_label_idx, str(gate_label_idx))
                parking_label = self.inv_parking_labels.get(parking_label_idx, str(parking_label_idx))

                gate_conf = float(np.max(gate_pred))
                parking_conf = float(np.max(parking_pred))

                # ✅ PATCH task to update data fields
                try:
                    self.project.update_task(
                        task.get('id'),
                        data={
                            **task['data'],
                            "prediction_gate_label": gate_label,
                            "prediction_parking_label": parking_label
                        }
                    )

                except Exception as update_error:
                    pass

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
                    'score': min(gate_conf, parking_conf),  # ✅ Label Studio uses this!
                    'meta': {
                        'model_version': self.model_version,
                        'confidence': {
                            'gate': gate_conf,
                            'parking': parking_conf
                        }
                    },
                    'extra': {
                        'prediction_gate_label': gate_label,
                        'prediction_parking_label': parking_label
                    }
                })
            except Exception as e:
                logging.error(f'Prediction error for task {task.get("id")}: {e}')
                logging.error(e)
                results.append({
                    'result': [],
                    'extra': {'error': str(e)},
                    'model_version': getattr(self, 'model_version', 'unknown')
                })
        return results