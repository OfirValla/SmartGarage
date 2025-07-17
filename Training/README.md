# SmartGarage Training Repository

This repository contains all code and resources for training, validating, and testing the SmartGarage machine learning models.

## Repository Structure

- **TrainModel/**: Contains all scripts and modules for training the garage gate model, including data preprocessing, model building, and training utilities.
- **LiveModelValidation/**: Standalone project for real-time validation of the trained model using a camera feed and TensorFlow Lite. See its own README for details.
- **LabelStudioModelValidation/**: (If present) Utilities for validating models using data from Label Studio.

## Quick Start

### 1. Training the Model
See `TrainModel/README.md` for instructions on how to train a new model.

### 2. Live Model Validation
See `LiveModelValidation/README.md` for instructions on how to run live validation with a camera feed.

### 3. Label Studio Model Validation
See `LabelStudioModelValidation/README.md` (if present) for instructions on validating with Label Studio data.

## Requirements
- Python 3.7+
- See each subproject's `requirements.txt` for dependencies.

## Notes
- Each subproject is self-contained and can be used independently.
- Environment variables and configuration are managed per subproject.

---
For more details, refer to the README in each subfolder. 