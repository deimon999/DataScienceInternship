# Task 1: ETL Pipeline Development

## Overview
This task involves building a Python-based ETL (Extract, Transform, Load) pipeline using **pandas** and **scikit-learn** for data preprocessing and transformation.

## Objective
To clean, transform, and prepare raw data for machine learning by:
- Removing duplicates
- Handling missing values
- Scaling numeric features
- Encoding categorical features
- Saving transformed data to CSV

## Files
- `etl_pipeline.py` - Main ETL pipeline script
- `requirements.txt` - Project dependencies

## Features
✓ **Data Preprocessing**
  - Remove duplicate rows
  - Handle missing values with median/most frequent imputation

✓ **Feature Transformation**
  - StandardScaler for numeric columns
  - OneHotEncoder for categorical columns

✓ **Scikit-learn Pipeline**
  - ColumnTransformer for parallel processing
  - Consistent and reusable preprocessing steps

✓ **Data Loading**
  - Save transformed data as CSV
  - Preserve feature names for reference

## Dependencies
```
pandas>=1.3.0
scikit-learn>=1.0.0
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python etl_pipeline.py --input input_data.csv --output output/transformed_data.csv
```

### Parameters
- `--input` (required): Path to input CSV file
- `--output` (optional): Path to output CSV file (default: `output/transformed_data.csv`)

## Example Output
```
Input rows: 1000
Output shape: (1000, 45)
Saved transformed data to: output/transformed_data.csv
```

## Key Learning Outcomes
- Understanding ETL workflow and data pipeline design
- Data preprocessing techniques and best practices
- Using scikit-learn transformers and pipelines
- Handling numeric and categorical data appropriately
- Building reusable and maintainable preprocessing code

## Technologies Used
- Python 3.x
- pandas (data manipulation)
- scikit-learn (preprocessing and transformation)
