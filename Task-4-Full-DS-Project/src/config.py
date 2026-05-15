"""
Configuration module for the House Price Prediction application.
Centralized settings management for the entire application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Model Configuration
from pathlib import Path as _Path

# Ensure model filenames are placed under MODEL_DIR even if env var contains a path
MODEL_PATH = MODEL_DIR / _Path(os.getenv("MODEL_PATH", "best_model.pkl")).name
PREPROCESSOR_PATH = MODEL_DIR / _Path(os.getenv("PREPROCESSOR_PATH", "preprocessor.pkl")).name
SCALER_PATH = MODEL_DIR / "scaler.pkl"
FEATURE_SELECTOR_PATH = MODEL_DIR / "feature_selector.pkl"

# Data Configuration
TRAIN_DATA_PATH = DATA_DIR / "train.csv"
TEST_DATA_PATH = DATA_DIR / "test.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed"
PROCESSED_DATA_PATH.mkdir(exist_ok=True)

# Feature Engineering
FEATURE_SCALING = os.getenv("FEATURE_SCALING", "standard")
MISSING_VALUE_STRATEGY = os.getenv("MISSING_VALUE_STRATEGY", "median")

# Model Training Configuration
TEST_SIZE = float(os.getenv("TEST_SIZE", 0.2))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", 42))
N_JOBS = int(os.getenv("N_JOBS", -1))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "app.log")

# Model Training Hyperparameters
XGBOOST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": RANDOM_STATE,
    "n_jobs": N_JOBS,
}

LIGHTGBM_PARAMS = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 6,
    "num_leaves": 31,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": RANDOM_STATE,
    "n_jobs": N_JOBS,
}

CATBOOST_PARAMS = {
    "iterations": 200,
    "learning_rate": 0.05,
    "depth": 6,
    "random_state": RANDOM_STATE,
    "verbose": 0,
    "thread_count": -1,
}

# Feature Selection
USE_FEATURE_SELECTION = True
N_FEATURES_TO_SELECT = 20

# Prediction Configuration
MIN_PRICE = 50000
MAX_PRICE = 500000
