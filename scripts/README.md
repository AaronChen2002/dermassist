# ML Scripts

This directory contains one-off scripts used for preparing data and training the machine learning model.

## Files

- `prepare_data.py`: This script handles all the logic for data acquisition and preparation. It downloads the HAM10000 dataset from Kaggle, unzips it, organizes the file structure, and then creates stratified `train.csv` and `val.csv` splits for balanced model training.

- `train.py`: This script contains the complete PyTorch training pipeline. It defines the `SkinLesionDataset`, sets up data augmentations, initializes the `MobileNetV2` model with a custom classifier head, and runs the training and validation loops. The best performing model weights are saved to the `models/` directory. 