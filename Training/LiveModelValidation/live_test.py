import os
import json
import numpy as np
import cv2
import tensorflow as tf
import config
import time

class CameraHandler:
    """Handles camera connection and management."""
    
    def __init__(self, rtsp_url=None, verbose=None):
        self.rtsp_url = rtsp_url or config.camera_rtsp_url
        self.video_capture = None
        self.call_counter = 0
        self._verbose = config.live_test_verbose if verbose is None else verbose
        print("Camera handler initialized")

    def camera(self, reset=False):
        self.call_counter += 1
        if self.call_counter == config.camera_refresh_interval or reset:
            if self._verbose:
                print('Refreshing camera connection')
                print(' * Closing connection')
            self.call_counter = 0
            if self.video_capture is not None:
                self.video_capture.release()
            self.video_capture = None
        if self.video_capture is None:
            if self._verbose:
                print(f' * Connecting to camera: {self.rtsp_url}')
            self.video_capture = cv2.VideoCapture(self.rtsp_url, apiPreference=cv2.CAP_FFMPEG)
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
        return self.video_capture

    def release(self):
        if self.video_capture:
            self.video_capture.release()

class LiveTester:
    """Class for live testing of the garage gate model (TFLite)."""
    def __init__(self, model_dir=None, rtsp_url=None):
        self.model_dir = model_dir or self._find_latest_model_dir()
        self.rtsp_url = rtsp_url or config.camera_rtsp_url
        self.tflite_model_path = os.path.join(self.model_dir, "garage_multi_output_model.tflite")
        self.gate_labels = self._load_labels(os.path.join(self.model_dir, "gate_labels.json"))
        self.parking_labels = self._load_labels(os.path.join(self.model_dir, "parking_labels.json"))
        self.gate_labels_inv = {v: k for k, v in self.gate_labels.items()}
        self.parking_labels_inv = {v: k for k, v in self.parking_labels.items()}
        print(f"Loaded gate label map: {self.gate_labels}")
        print(f"Loaded parking label map: {self.parking_labels}")
        print(f"Gate label indices: {list(self.gate_labels_inv.keys())}")
        print(f"Parking label indices: {list(self.parking_labels_inv.keys())}")
        self.interpreter = tf.lite.Interpreter(model_path=self.tflite_model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        print("TFLite output details:")
        for i, detail in enumerate(self.output_details):
            print(f"  Output {i}: {detail['name']}")
            print(f"  Output {i}: {detail}")
        self.camera_handler = CameraHandler(self.rtsp_url)
        self.last_gate_label = ''
        self.last_parking_label = ''
        os.makedirs(config.live_test_predictions_dir, exist_ok=True)

    def _find_latest_model_dir(self):
        output_root = "../output"
        version_dirs = [d for d in os.listdir(output_root) if d.startswith("V")]
        if not version_dirs:
            raise FileNotFoundError("No versioned model directories found in output/")
        latest_version = sorted(version_dirs)[-1]
        return os.path.join(output_root, latest_version)

    def _load_labels(self, label_path):
        with open(label_path, "r") as f:
            labels = json.load(f)
        return {str(k): int(v) for k, v in labels.items()}

    def preprocess_frame(self, frame):
        img = cv2.resize(frame, (360, 640))
        if img.ndim == 2:
            img = np.expand_dims(img, axis=-1)
        if img.shape[-1] == 1:
            img = np.repeat(img, 3, axis=-1)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img

    def run_live_test(self):
        print("Starting live testing with TFLite model...")
        print("Press 'q' to quit")
        while True:
            ret, frame = self.camera_handler.camera().read()
            if frame is None:
                print("No frame received from camera")
                continue
            processed_frame = self.preprocess_frame(frame)
            self.interpreter.set_tensor(self.input_details[0]['index'], processed_frame)
            self.interpreter.invoke()
            parking_pred = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            gate_pred = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
            gate_label_idx = int(np.argmax(gate_pred))
            parking_label_idx = int(np.argmax(parking_pred))
            gate_label = self.gate_labels_inv.get(gate_label_idx)
            parking_label = self.parking_labels_inv.get(parking_label_idx)
            if gate_label is None:
                print(f"[WARNING] Gate label index {gate_label_idx} not found in label map! Known indices: {list(self.gate_labels_inv.keys())}")
                gate_label = f"Unknown({gate_label_idx})"
            if parking_label is None:
                print(f"[WARNING] Parking label index {parking_label_idx} not found in label map! Known indices: {list(self.parking_labels_inv.keys())}")
                parking_label = f"Unknown({parking_label_idx})"
            gate_conf = gate_pred[gate_label_idx] * 100
            parking_conf = parking_pred[parking_label_idx] * 100
            if self.last_gate_label != gate_label or self.last_parking_label != parking_label:
                self.last_gate_label = gate_label
                self.last_parking_label = parking_label
                print(f'Gate: {gate_label} ({gate_conf:.1f}%) | Parking: {parking_label} ({parking_conf:.1f}%)')
                if config.live_test_save_images:
                    epoch_ms = int(time.time() * 1000)
                    filename = f'{epoch_ms}_gate_{gate_label}_{gate_conf:.1f}_parking_{parking_label}_{parking_conf:.1f}.jpg'
                    filepath = os.path.join(config.live_test_predictions_dir, filename)
                    cv2.imwrite(filepath, frame)
            cv2.putText(frame, f'Gate: {gate_label} ({gate_conf:.1f}%)', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f'Parking: {parking_label} ({parking_conf:.1f}%)', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Garage Gate Status', frame)
            delay = 1.0 / config.live_test_fps
            elapsed = 0
            interrupted = False
            while elapsed < delay:
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    interrupted = True
                    break
                time.sleep(0.01)
                elapsed += 0.01
            if interrupted:
                break
        self.camera_handler.release()
        cv2.destroyAllWindows()
        print("Live testing stopped")

def main():
    print("=== Garage Gate Model Live Testing (TFLite) ===")
    tester = LiveTester()
    tester.run_live_test()

if __name__ == "__main__":
    main() 