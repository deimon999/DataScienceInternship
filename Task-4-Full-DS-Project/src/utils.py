"""
Utility functions for data processing and model management.
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import Any, Union, Dict, List, Tuple
from .logger_setup import logger


def save_model(model: Any, path: Union[str, Path]) -> None:
    """
    Save a model to disk using pickle.
    
    Args:
        model: Model object to save
        path: File path to save the model
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model saved successfully to {path}")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise


def load_model(path: Union[str, Path]) -> Any:
    """
    Load a model from disk.
    
    Args:
        path: File path to the saved model
        
    Returns:
        Loaded model object
    """
    try:
        path = Path(path)
        with open(path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded successfully from {path}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def calculate_statistics(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for a dataset.
    
    Args:
        data: Input dataframe
        
    Returns:
        Dictionary containing various statistics
    """
    stats = {
        "shape": data.shape,
        "memory_usage_mb": data.memory_usage(deep=True).sum() / 1024**2,
        "missing_values": data.isnull().sum().to_dict(),
        "numeric_summary": data.describe().to_dict(),
        "dtypes": data.dtypes.to_dict(),
    }
    return stats


def validate_input_features(data: Dict[str, Any], required_features: List[str]) -> Tuple[bool, str]:
    """
    Validate that input contains all required features.
    
    Args:
        data: Input dictionary
        required_features: List of required feature names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_features = set(required_features) - set(data.keys())
    
    if missing_features:
        return False, f"Missing features: {missing_features}"
    
    # Check for reasonable value ranges
    for feature, value in data.items():
        if isinstance(value, (int, float)):
            if not (-1e9 < value < 1e9):
                return False, f"Feature {feature} has unrealistic value: {value}"
    
    return True, "Input validation passed"


def calculate_feature_importance_summary(importances: np.ndarray, feature_names: List[str], top_n: int = 10) -> Dict[str, float]:
    """
    Calculate and return top N important features.
    
    Args:
        importances: Feature importance array
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        Dictionary of feature names and importance scores
    """
    if len(importances) != len(feature_names):
        logger.error("Importance array length doesn't match feature names")
        return {}
    
    importance_dict = dict(zip(feature_names, importances))
    sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    
    return dict(sorted_features[:top_n])


def detect_outliers(data: pd.Series, method: str = "iqr", threshold: float = 1.5) -> np.ndarray:
    """
    Detect outliers in a series using IQR or Z-score method.
    
    Args:
        data: Input series
        method: "iqr" or "zscore"
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean array indicating outliers
    """
    if method == "iqr":
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == "zscore":
        from scipy import stats
        z_scores = np.abs(stats.zscore(data.dropna()))
        return z_scores > threshold
    
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")


def evaluate_prediction(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary of evaluation metrics
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    # Mean Absolute Percentage Error
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    return {
        "mse": float(mse),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2_score": float(r2),
        "mape": float(mape),
    }


def check_data_drift(reference_data: pd.DataFrame, new_data: pd.DataFrame, 
                     threshold: float = 0.05) -> Dict[str, Any]:
    """
    Check for data drift between reference and new data.
    
    Args:
        reference_data: Reference dataset
        new_data: New dataset to check
        threshold: Drift threshold
        
    Returns:
        Dictionary with drift information
    """
    drift_report = {
        "drifted_features": [],
        "feature_stats": {}
    }
    
    numeric_cols = new_data.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col not in reference_data.columns:
            continue
        
        ref_mean = reference_data[col].mean()
        new_mean = new_data[col].mean()
        
        # Simple drift detection using mean change percentage
        if ref_mean != 0:
            change_percent = abs((new_mean - ref_mean) / ref_mean)
            if change_percent > threshold:
                drift_report["drifted_features"].append(col)
            
            drift_report["feature_stats"][col] = {
                "reference_mean": float(ref_mean),
                "new_mean": float(new_mean),
                "change_percent": float(change_percent),
            }
    
    return drift_report
