# Task 2: Deep Learning Project - CNN Image Classification

## Overview
This task involves building a Convolutional Neural Network (CNN) to classify handwritten digits from the **MNIST dataset** using **TensorFlow/Keras**.

## Objective
To develop a deep learning model that:
- Classifies images into 10 digit categories (0-9)
- Achieves high accuracy on the MNIST dataset
- Generates training visualizations and evaluation metrics
- Saves the trained model for future use

## Files
- `task2_deep_learning.py` - Main deep learning training and evaluation script
- `mnist_cnn.keras` - Trained model (generated after running)
- `training_curves.png` - Accuracy and loss curves (generated after running)
- `confusion_matrix.png` - Evaluation metrics visualization (generated after running)

## Model Architecture
```
Input Layer: 28x28x1 (MNIST image size)
    ↓
Conv2D (32 filters, kernel=3x3, ReLU)
    ↓
MaxPooling2D (2x2)
    ↓
Conv2D (64 filters, kernel=3x3, ReLU)
    ↓
MaxPooling2D (2x2)
    ↓
Flatten Layer
    ↓
Dense (128 units, ReLU)
    ↓
Dropout (0.3)
    ↓
Dense (10 units, Softmax) → Output
```

## Dependencies
```
tensorflow>=2.10.0
keras>=2.10.0
numpy>=1.21.0
matplotlib>=3.4.0
scikit-learn>=1.0.0
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python task2_deep_learning.py --epochs 10 --batch-size 128 --output-dir task2_output
```

### Parameters
- `--epochs` (optional): Number of training epochs (default: 3)
- `--batch-size` (optional): Batch size for training (default: 128)
- `--output-dir` (optional): Directory to save outputs (default: `task2_output`)

## Example Output
```
Epoch 1/10
...
Epoch 10/10
Test loss: 0.0532
Test accuracy: 0.9825
Saved model and plots in: task2_output
```

## Output Files Generated
1. **mnist_cnn.keras** - Trained model file (can be loaded and used for inference)
2. **training_curves.png** - Shows accuracy and loss over epochs
3. **confusion_matrix.png** - Shows classification accuracy per digit

## Key Learning Outcomes
- Understanding CNN architecture and layers
- Image preprocessing and normalization
- Model training and validation techniques
- Performance evaluation using confusion matrix
- Visualizing training metrics and results
- Saving and loading trained models

## Performance Metrics
- **Training Accuracy**: ~99%
- **Test Accuracy**: ~98%
- **Loss Function**: Sparse Categorical Crossentropy
- **Optimizer**: Adam

## Technologies Used
- Python 3.x
- TensorFlow/Keras (deep learning framework)
- NumPy (numerical computations)
- Matplotlib (visualization)
- Scikit-learn (metrics and evaluation)

## Notes
- The MNIST dataset is automatically downloaded on first run
- Training takes a few minutes depending on epochs and hardware
- GPU acceleration recommended for faster training
