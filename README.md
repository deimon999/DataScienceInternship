# Internship Task 1: Data Pipeline Development

This submission implements a Python ETL pipeline using `pandas` and `scikit-learn` for:

- Data preprocessing (duplicates and missing values)
- Data transformation (scaling numeric features and encoding categorical features)
- Data loading (saving transformed dataset to CSV)

## Files

- `etl_pipeline.py`: Main ETL script
- `requirements.txt`: Dependencies

## Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the pipeline:

```bash
python etl_pipeline.py --input your_data.csv --output output/transformed_data.csv
```

If `--output` is not provided, the default is `output/transformed_data.csv`.

---

# Internship Task 2: Deep Learning Project

This submission implements an image classification model using TensorFlow (CNN on MNIST) with required visualizations.

## Files

- `task2_deep_learning.py`: Training and evaluation script

## Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Train and generate outputs:

```bash
python task2_deep_learning.py --epochs 3 --batch-size 128 --output-dir task2_output
```

## Output Artifacts

After running, the script saves:

- `task2_output/mnist_cnn.keras` (trained model)
- `task2_output/training_curves.png` (accuracy/loss visualization)
- `task2_output/confusion_matrix.png` (result visualization)
