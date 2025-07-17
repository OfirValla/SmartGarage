# Garage Gate Model

A machine learning project for classifying garage gate states using computer vision.

## Project Structure

The project is organized into modular components:

### 📁 Training Module (`training/`)
- **`train_model.py`** - Main training script
- Handles dataset splitting, model training, and model saving (including TFLite export and label maps)
- Uses shared utilities for preprocessing and model creation

### 📁 Shared Utilities (`shared/`)
- **`preprocessing.py`** - Common image preprocessing functions
- **`config.py`** - Centralized configuration (including environment variable support)
- **`label_studio_utils.py`** - Label Studio integration

## Quick Start

### Training the Model
```bash
python main.py train
```

## Detailed Usage

### Training
The training module will:
1. Load and preprocess training and validation data from Label Studio
2. Create and train a multi-output CNN model
3. Save the trained model in a versioned output directory (`output/V{date}/`):
   - SavedModel format
   - TFLite model (`garage_multi_output_model.tflite`)
   - Label maps (`gate_labels.json`, `parking_labels.json`)
   - Model summary (`model_summary.txt`)

## File Structure
```
TrainModel/
├── main.py                 # Main entry point
├── training/
│   ├── __init__.py
│   ├── train_model.py      # Training script
│   ├── data_generator.py   # Data pipeline
│   ├── model_builder.py    # Model architecture
│   └── trainer.py          # Training/export logic
├── validation/
│   ├── __init__.py
├── shared/
│   ├── __init__.py
│   ├── preprocessing.py    # Image preprocessing
│   ├── config.py           # Configuration
│   └── label_studio_utils.py # Label Studio integration
├── output/                 # Versioned model exports
├── Dataset/                # Dataset directory
```

## Requirements

- Python 3.7+
- TensorFlow
- OpenCV
- NumPy
- scikit-learn
- python-dotenv
- label-studio-sdk

## Configuration

### Dataset Structure
Expected dataset structure:
```
Dataset/
├── dataset/               # Original dataset
│   ├── Closed/
│   ├── Open/
│   └── OpeningOrClosing/
├── splitted-dataset/      # Auto-generated split
│   ├── train/
│   └── val/
└── Test/                  # Test images
```

## Model Export & Label Maps
- Each training run creates a new versioned folder in `output/`.
- Both the TFLite model and the label maps are saved for robust deployment and testing.
- The model summary is saved as `model_summary.txt` for reference.

## .gitignore
A `.gitignore` file is included to exclude:
- Bytecode, cache, and virtual environments
- Model outputs and logs (`output/`, `garage_gate_model/`, etc.)
- IDE/project files and OS-specific files
- Environment variable files (`.env`)

## Benefits of the Structure

1. **Separation of Concerns**: Training and validation are modular
2. **Reproducibility**: Versioned model and label exports
3. **Configurability**: All key parameters are environment-driven
4. **Maintainability**: Easy to extend and debug
5. **Clarity**: Clear organization and documentation

## Migration from Old Structure

The original files have been refactored and improved for modularity and maintainability. All functionality is preserved while improving code organization and reusability. 