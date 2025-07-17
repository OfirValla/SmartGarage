from shared.label_studio_utils import LabelStudioManager
from .data_generator import create_dataset, split_dataset, count_samples
from .model_builder import create_model
from .trainer import train_model, export_model

def main():
    print("=== Garage Gate Model Training ===")
    
    # Initialize Label Studio manager
    ls_manager = LabelStudioManager()
    
    # Get label configurations
    gate_label_map, parking_label_map = ls_manager.get_label_config_info()
    print(f"Gate labels: {gate_label_map.keys()} ({len(gate_label_map)})")
    print(f"Parking labels: {parking_label_map.keys()} ({len(parking_label_map)})")

    # Create dataset
    dataset = create_dataset(ls_manager, gate_label_map, parking_label_map)

    # Count samples and split dataset
    num_samples = count_samples(ls_manager, gate_label_map, parking_label_map)
    print(f"✅ Total labeled samples: {num_samples}")

    train_dataset, val_dataset = split_dataset(dataset, num_samples)

    # Create and compile model
    model = create_model(len(gate_label_map), len(parking_label_map))
    
    # Train model
    train_model(model, train_dataset, val_dataset, epochs=10)

    # Export model
    export_model(model, gate_label_map, parking_label_map)

    print("🎉 Training pipeline completed successfully!")

if __name__ == "__main__":
    main() 