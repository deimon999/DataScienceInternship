"""
Integration tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from api import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data


class TestPredictionEndpoints:
    """Test prediction endpoints."""

    def test_single_prediction_valid(self):
        """Test single prediction with valid input."""
        payload = {
            "square_feet": 2500,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "age": 10,
            "garage": 2,
            "location_score": 8.5,
            "condition": "good"
        }
        
        response = client.post("/predict", json=payload)
        
        if response.status_code == 503:
            # Model not loaded, skip
            pytest.skip("Model not loaded")
        
        assert response.status_code == 200
        data = response.json()
        assert "predicted_price" in data
        assert "confidence" in data
        assert "prediction_range" in data

    def test_single_prediction_invalid_condition(self):
        """Test single prediction with invalid condition."""
        payload = {
            "square_feet": 2500,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "age": 10,
            "garage": 2,
            "location_score": 8.5,
            "condition": "invalid"
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error

    def test_batch_prediction(self):
        """Test batch prediction."""
        payload = {
            "data": [
                {
                    "square_feet": 2500,
                    "bedrooms": 4,
                    "bathrooms": 2.5,
                    "age": 10,
                    "garage": 2,
                    "location_score": 8.5,
                    "condition": "good"
                },
                {
                    "square_feet": 3000,
                    "bedrooms": 5,
                    "bathrooms": 3.0,
                    "age": 5,
                    "garage": 3,
                    "location_score": 9.0,
                    "condition": "excellent"
                }
            ]
        }
        
        response = client.post("/batch-predict", json=payload)
        
        if response.status_code == 503:
            pytest.skip("Model not loaded")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_predictions"] == 2
        assert "predictions" in data
        assert "average_price" in data

    def test_batch_prediction_empty(self):
        """Test batch prediction with empty data."""
        payload = {"data": []}
        
        response = client.post("/batch-predict", json=payload)
        assert response.status_code == 400


class TestModelInfoEndpoints:
    """Test model information endpoints."""

    def test_model_info(self):
        """Test model info endpoint."""
        response = client.get("/model-info")
        
        if response.status_code == 503:
            pytest.skip("Model not loaded")
        
        assert response.status_code == 200
        data = response.json()
        assert "model_type" in data

    def test_feature_importance(self):
        """Test feature importance endpoint."""
        response = client.get("/feature-importance?top_n=10")
        
        if response.status_code == 503:
            pytest.skip("Model not loaded")
        
        # Some models don't support feature importance
        if response.status_code != 400:
            assert response.status_code == 200
            data = response.json()
            assert "top_features" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
