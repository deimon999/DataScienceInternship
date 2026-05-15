"""
Unit tests for the API and core modules.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_pipeline import AdvancedPreprocessor
from model_training import ModelTrainer
from utils import (
    save_model, load_model, validate_input_features,
    evaluate_prediction, detect_outliers
)


class TestDataPipeline:
    """Test data preprocessing pipeline."""

    def setup_method(self):
        """Setup test fixtures."""
        self.preprocessor = AdvancedPreprocessor()
        self.sample_df = pd.DataFrame({
            'square_feet': [2000, 2500, 1500, 3000],
            'bedrooms': [3, 4, 2, 5],
            'bathrooms': [2.0, 2.5, 1.5, 3.0],
            'age': [10, 20, 5, 15],
            'garage': [2, 2, 1, 3],
            'location_score': [7.5, 8.0, 6.5, 8.5],
            'condition': ['good', 'excellent', 'fair', 'good'],
            'Price': [400000, 450000, 300000, 500000]
        })

    def test_missing_value_handling(self):
        """Test missing value imputation."""
        df = self.sample_df.copy()
        df.loc[0, 'bedrooms'] = np.nan
        
        processed = self.preprocessor.handle_missing_values(df)
        assert processed['bedrooms'].isnull().sum() == 0

    def test_feature_identification(self):
        """Test numeric and categorical feature identification."""
        numeric, categorical = self.preprocessor.identify_feature_types(self.sample_df)
        
        assert 'bedrooms' in numeric
        assert 'condition' in categorical
        assert len(numeric) > 0
        assert len(categorical) > 0

    def test_outlier_detection(self):
        """Test outlier detection."""
        df = self.sample_df.copy()
        df.loc[0, 'square_feet'] = 50000  # Extreme outlier
        
        processed = self.preprocessor.detect_and_handle_outliers(df)
        assert processed.loc[0, 'square_feet'] < 10000  # Should be capped


class TestModelTraining:
    """Test model training module."""

    def setup_method(self):
        """Setup test fixtures."""
        self.trainer = ModelTrainer()
        
        # Create dummy data
        np.random.seed(42)
        self.X_train = pd.DataFrame({
            f'feature_{i}': np.random.randn(100) for i in range(5)
        })
        self.y_train = pd.Series(np.random.randn(100) * 100000 + 300000)

    def test_model_creation(self):
        """Test model creation."""
        models = {
            'xgboost': self.trainer.build_xgboost_model(),
            'lightgbm': self.trainer.build_lightgbm_model(),
            'catboost': self.trainer.build_catboost_model(),
        }
        
        assert all(model is not None for model in models.values())

    def test_model_training(self):
        """Test model training."""
        cv_scores = self.trainer.train_models(self.X_train, self.y_train)
        
        assert len(cv_scores) > 0
        assert all(isinstance(score, (int, float)) for score in cv_scores.values())

    def test_model_prediction(self):
        """Test model prediction."""
        self.trainer.train_models(self.X_train, self.y_train)
        predictions = self.trainer.predict(self.X_train)
        
        assert len(predictions) == len(self.X_train)
        assert all(isinstance(p, (int, float)) for p in predictions)


class TestUtils:
    """Test utility functions."""

    def test_validate_input_features(self):
        """Test input validation."""
        valid_input = {'feature1': 10, 'feature2': 20}
        required = ['feature1', 'feature2']
        
        is_valid, msg = validate_input_features(valid_input, required)
        assert is_valid

    def test_invalid_input_features(self):
        """Test invalid input detection."""
        invalid_input = {'feature1': 10}
        required = ['feature1', 'feature2']
        
        is_valid, msg = validate_input_features(invalid_input, required)
        assert not is_valid

    def test_outlier_detection(self):
        """Test outlier detection."""
        data = pd.Series([1, 2, 3, 4, 5, 1000])  # 1000 is outlier
        
        outliers = detect_outliers(data, method='iqr')
        assert outliers.sum() > 0

    def test_evaluate_prediction(self):
        """Test evaluation metrics."""
        y_true = np.array([100, 200, 300, 400, 500])
        y_pred = np.array([110, 190, 310, 390, 520])
        
        metrics = evaluate_prediction(y_true, y_pred)
        
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'r2_score' in metrics


class TestModelPersistence:
    """Test model saving and loading."""

    def test_save_and_load_model(self, tmp_path):
        """Test model persistence."""
        model = ModelTrainer().build_xgboost_model()
        
        # Create dummy data and train
        X = pd.DataFrame({f'feature_{i}': np.random.randn(50) for i in range(5)})
        y = pd.Series(np.random.randn(50) * 100000 + 300000)
        model.fit(X, y)
        
        # Save
        model_path = tmp_path / "test_model.pkl"
        save_model(model, model_path)
        
        # Load
        loaded_model = load_model(model_path)
        
        # Verify
        assert loaded_model is not None
        pred1 = model.predict(X[:5])
        pred2 = loaded_model.predict(X[:5])
        
        np.testing.assert_array_almost_equal(pred1, pred2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
