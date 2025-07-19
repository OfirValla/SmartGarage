import os
import tensorflow as tf
from datetime import datetime
import json

def train_model(model, train_dataset, val_dataset, epochs=10):
    """Train the model and return training history."""
    print(f"🚀 Starting training for {epochs} epochs...")
    
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=epochs,
        verbose=1
    )
    
    print("✅ Training completed!")
    return history

def export_model(model, gate_label_map, parking_label_map, task_stats=None):
    """Export model to SavedModel and TFLite formats, and save label maps and task statistics as JSON."""
    def __create_output_directory():
        """Create versioned output directory based on current date."""
        current_date = datetime.now()
        version = f"V{current_date.day}.{current_date.month}.{current_date.year}"
        output_dir = os.path.join("../output", version)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir 

    output_dir = __create_output_directory()
    print(f"📁 Saving model to: {output_dir}")
    
    # Save SavedModel format
    model_path = os.path.join(output_dir, "garage_multi_output_model")
    model.export(model_path)

    # Convert and save TFLite format
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    tflite_model = converter.convert()
    tflite_path = os.path.join(output_dir, "garage_multi_output_model.tflite")
    with open(tflite_path, "wb") as f:
        f.write(tflite_model)

    # Save label maps as JSON
    with open(os.path.join(output_dir, "gate_labels.json"), "w") as f:
        json.dump(gate_label_map, f)
    with open(os.path.join(output_dir, "parking_labels.json"), "w") as f:
        json.dump(parking_label_map, f)

    # Save task statistics if provided
    if task_stats:
        with open(os.path.join(output_dir, "task_statistics.json"), "w") as f:
            json.dump(task_stats.to_dict(), f, indent=2)

    # Save model summary to a text file
    summary_path = os.path.join(output_dir, "model_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        model.summary(print_fn=lambda x: f.write(x + "\n"))

    print(f"✅ Model and labels exported successfully!")
    print(f"   - SavedModel: {model_path}")
    print(f"   - TFLite: {tflite_path}")
    print(f"   - Gate labels: gate_labels.json")
    print(f"   - Parking labels: parking_labels.json")
    print(f"   - Task statistics: task_statistics.json")
    
    return model_path, tflite_path