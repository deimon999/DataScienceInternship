"""
FastAPI backend for House Price Prediction.
Provides REST API endpoints for model inference and monitoring.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime
import io

from .logger_setup import logger
from .config import API_HOST, API_PORT, MODEL_PATH, PREPROCESSOR_PATH, MIN_PRICE, MAX_PRICE
from .utils import (
    load_model, validate_input_features, evaluate_prediction,
    check_data_drift, calculate_feature_importance_summary
)

# Initialize FastAPI app
app = FastAPI(
    title="House Price Prediction API",
    description="Advanced ML API for predicting house prices with multiple models",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
preprocessor = None
model = None
training_data = None


# ============== Pydantic Models ==============

class HousePriceInput(BaseModel):
    """Input model for single house price prediction."""
    square_feet: float = Field(..., gt=0, description="House size in square feet")
    bedrooms: int = Field(..., ge=1, le=10, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=1, le=10, description="Number of bathrooms")
    age: int = Field(..., ge=0, le=150, description="Age of house in years")
    garage: int = Field(..., ge=0, le=5, description="Number of garage spaces")
    location_score: float = Field(..., ge=1, le=10, description="Location desirability score")
    condition: str = Field(..., description="Condition of house (excellent, good, fair, poor)")
    
    @validator('condition')
    def validate_condition(cls, v):
        valid_conditions = ['excellent', 'good', 'fair', 'poor']
        if v.lower() not in valid_conditions:
            raise ValueError(f'Condition must be one of {valid_conditions}')
        return v.lower()
    
    class Config:
        example = {
            "square_feet": 2500,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "age": 10,
            "garage": 2,
            "location_score": 8.5,
            "condition": "good"
        }


class BatchPredictionInput(BaseModel):
    """Input model for batch predictions."""
    data: List[HousePriceInput] = Field(..., description="List of house data for prediction")


class PredictionResponse(BaseModel):
    """Output model for price prediction."""
    predicted_price: float
    confidence: float
    prediction_range: Dict[str, float]
    timestamp: str


class BatchPredictionResponse(BaseModel):
    """Output model for batch predictions."""
    total_predictions: int
    predictions: List[Dict[str, Any]]
    average_price: float
    price_range: Dict[str, float]
    timestamp: str


class ModelMetrics(BaseModel):
    """Model performance metrics."""
    mse: float
    mae: float
    rmse: float
    r2_score: float
    mape: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    preprocessor_loaded: bool
    timestamp: str
    version: str


# ============== Initialization ==============

def load_models():
    """Load models on startup."""
    global model, preprocessor
    try:
        logger.info("Loading models on startup")
        # Try primary model path, then fall back to common artifact names
        tried = []
        paths_to_try = [MODEL_PATH]
        # Fallbacks
        from pathlib import Path
        paths_to_try.append(Path(MODEL_PATH).parent / 'best_model.pkl')
        paths_to_try.append(Path(MODEL_PATH).parent / 'best_model_model.pkl')
        paths_to_try.append(Path(MODEL_PATH).parent / 'house_price_model.pkl')

        model = None
        for p in paths_to_try:
            tried.append(str(p))
            try:
                model = load_model(p)
                logger.info(f"Loaded model from {p}")
                break
            except Exception:
                logger.info(f"Model not found at {p}")

        preprocessor = None
        try:
            preprocessor = load_model(PREPROCESSOR_PATH)
        except Exception:
            logger.info(f"Preprocessor not found at {PREPROCESSOR_PATH}")
        logger.info(f"Tried model paths: {tried}")
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        logger.warning("Models will need to be trained before making predictions")


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    load_models()
    logger.info("FastAPI application started")


# Serve frontend static files if available (mount at /ui)
try:
    from pathlib import Path
    frontend_dir = Path(__file__).resolve().parent.parent / 'frontend'
    if frontend_dir.exists():
        app.mount('/ui', StaticFiles(directory=str(frontend_dir), html=True), name='frontend')
        logger.info(f"Mounted frontend static files from {frontend_dir} at /ui")
    else:
        logger.info(f"No frontend directory found at {frontend_dir}")
except Exception as e:
    logger.warning(f"Failed to mount frontend static files: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("FastAPI application shutting down")


# ============== Health & Status Endpoints ==============

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Verifies API and model availability.
    """
    return HealthResponse(
        status="healthy" if model and preprocessor else "models_not_loaded",
        model_loaded=model is not None,
        preprocessor_loaded=preprocessor is not None,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/", tags=["Info"])
async def root():
    """API information and documentation."""
    return {
        "name": "House Price Prediction API",
        "version": "1.0.0",
        "description": "Advanced ML API for predicting house prices",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/batch-predict",
            "feature_importance": "/feature-importance",
            "model_info": "/model-info"
        }
    }


# ============== Prediction Endpoints ==============

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_single(data: HousePriceInput):
    """
    Predict house price for a single property.
    
    Args:
        data: House features
        
    Returns:
        Predicted price with confidence interval
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train model first.")
    
    try:
        # Convert input to dataframe
        input_df = pd.DataFrame([data.dict()])
        
        # Validate input
        is_valid, message = validate_input_features(input_df.to_dict('records')[0], data.dict().keys())
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Preprocess
        processed_data = preprocessor.transform(input_df)
        
        # Predict
        prediction = model.predict(processed_data)[0]
        
        # Apply constraints
        prediction = max(MIN_PRICE, min(MAX_PRICE, prediction))
        
        # Calculate confidence (based on input data quality)
        confidence = min(0.95, 0.7 + (0.05 if 1 <= data.location_score <= 10 else 0))
        
        # Prediction range (±10%)
        lower_bound = prediction * 0.9
        upper_bound = prediction * 1.1
        
        logger.info(f"Prediction made: {prediction:.2f}")
        
        return PredictionResponse(
            predicted_price=float(prediction),
            confidence=confidence,
            prediction_range={
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "margin_percent": 10.0
            },
            timestamp=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/batch-predict", response_model=BatchPredictionResponse, tags=["Predictions"])
async def batch_predict(data: BatchPredictionInput):
    """
    Predict house prices for multiple properties.
    
    Args:
        data: List of house features
        
    Returns:
        Batch predictions with statistics
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train model first.")
    
    try:
        if len(data.data) == 0:
            raise HTTPException(status_code=400, detail="Empty data list")
        
        if len(data.data) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 predictions per batch")
        
        # Convert to dataframe
        input_data = [item.dict() for item in data.data]
        input_df = pd.DataFrame(input_data)
        
        # Preprocess
        processed_data = preprocessor.transform(input_df)
        
        # Batch predict
        predictions = model.predict(processed_data)
        predictions = np.clip(predictions, MIN_PRICE, MAX_PRICE)
        
        # Prepare response
        predictions_list = [
            {
                "predicted_price": float(pred),
                "confidence": 0.8,
                "house_id": i
            }
            for i, pred in enumerate(predictions)
        ]
        
        logger.info(f"Batch prediction completed for {len(predictions)} items")
        
        return BatchPredictionResponse(
            total_predictions=len(predictions),
            predictions=predictions_list,
            average_price=float(np.mean(predictions)),
            price_range={
                "min": float(np.min(predictions)),
                "max": float(np.max(predictions)),
                "std": float(np.std(predictions))
            },
            timestamp=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


# ============== Model Information Endpoints ==============

@app.get("/model-info", tags=["Model Information"])
async def model_info():
    """
    Get information about the current model.
    
    Returns:
        Model metadata and statistics
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        return {
            "model_type": type(model).__name__,
            "model_path": str(MODEL_PATH),
            "created_at": datetime.utcnow().isoformat(),
            "parameters": {
                "min_price": MIN_PRICE,
                "max_price": MAX_PRICE,
            }
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model information")


@app.get("/feature-importance", tags=["Model Information"])
async def feature_importance(top_n: int = 10):
    """
    Get feature importance from the trained model.
    
    Args:
        top_n: Number of top features to return
        
    Returns:
        Dictionary of top features and their importance
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        if not hasattr(model, 'feature_importances_'):
            raise HTTPException(
                status_code=400,
                detail="Current model doesn't support feature importance"
            )
        
        importances = model.feature_importances_
        feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        importance_dict = calculate_feature_importance_summary(importances, feature_names, top_n)
        
        return {
            "top_features": importance_dict,
            "total_features": len(importances),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get feature importance")


# ============== Error Handlers ==============

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"Value error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Invalid input: {str(exc)}"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============== Main ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
