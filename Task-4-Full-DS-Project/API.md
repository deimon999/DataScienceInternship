# API Documentation

## Overview

The House Price Prediction API provides endpoints for making price predictions, accessing model information, and batch processing. The API is built with FastAPI and follows RESTful conventions.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production, implement:
- API Key authentication
- JWT tokens
- OAuth2

## Response Format

All responses are in JSON format:

```json
{
  "status": "success",
  "data": {},
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Error Handling

Errors return appropriate HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 422 | Unprocessable Entity (invalid data) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (model not loaded) |

## Endpoints

### 1. Health Check

```
GET /health
```

Check if API and models are available.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "preprocessor_loaded": true,
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### 2. Single Price Prediction

```
POST /predict
Content-Type: application/json
```

Predict house price for a single property.

**Request Body:**
```json
{
  "square_feet": 2500,
  "bedrooms": 4,
  "bathrooms": 2.5,
  "age": 10,
  "garage": 2,
  "location_score": 8.5,
  "condition": "good"
}
```

**Response:**
```json
{
  "predicted_price": 425000.50,
  "confidence": 0.85,
  "prediction_range": {
    "lower_bound": 382500.45,
    "upper_bound": 467500.55,
    "margin_percent": 10.0
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid input
- 422: Validation error
- 503: Model not loaded

### 3. Batch Predictions

```
POST /batch-predict
Content-Type: application/json
```

Predict prices for multiple properties.

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "total_predictions": 2,
  "predictions": [
    {
      "predicted_price": 425000.50,
      "confidence": 0.85,
      "house_id": 0
    },
    {
      "predicted_price": 485000.75,
      "confidence": 0.87,
      "house_id": 1
    }
  ],
  "average_price": 455000.625,
  "price_range": {
    "min": 425000.50,
    "max": 485000.75,
    "std": 30000.125
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Limits:**
- Maximum 1000 properties per request
- Maximum request size: 10MB

### 4. Model Information

```
GET /model-info
```

Get information about the trained model.

**Response:**
```json
{
  "model_type": "XGBRegressor",
  "model_path": "./models/house_price_model.pkl",
  "created_at": "2024-01-01T12:00:00Z",
  "parameters": {
    "min_price": 50000,
    "max_price": 500000
  }
}
```

### 5. Feature Importance

```
GET /feature-importance?top_n=10
```

Get the most important features used by the model.

**Query Parameters:**
- `top_n` (int, default: 10): Number of top features to return

**Response:**
```json
{
  "top_features": {
    "square_feet": 0.35,
    "location_score": 0.25,
    "bedrooms": 0.18,
    "bathrooms": 0.12,
    "age": 0.10
  },
  "total_features": 12,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 6. API Root

```
GET /
```

Get API information and available endpoints.

**Response:**
```json
{
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
```

## Request Validation

### Field Requirements

| Field | Type | Range | Required |
|-------|------|-------|----------|
| square_feet | number | 1-∞ | ✓ |
| bedrooms | integer | 1-10 | ✓ |
| bathrooms | number | 1-10 | ✓ |
| age | integer | 0-150 | ✓ |
| garage | integer | 0-5 | ✓ |
| location_score | number | 1-10 | ✓ |
| condition | string | excellent, good, fair, poor | ✓ |

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "bedrooms"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

## Rate Limiting

Currently no rate limiting. For production, implement:
- Requests per minute per API key
- Requests per day
- Concurrent request limits

## CORS Headers

The API includes CORS headers for cross-origin requests:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## cURL Examples

### Single Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "square_feet": 2500,
    "bedrooms": 4,
    "bathrooms": 2.5,
    "age": 10,
    "garage": 2,
    "location_score": 8.5,
    "condition": "good"
  }'
```

### Batch Prediction
```bash
curl -X POST "http://localhost:8000/batch-predict" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "square_feet": 2500,
        "bedrooms": 4,
        "bathrooms": 2.5,
        "age": 10,
        "garage": 2,
        "location_score": 8.5,
        "condition": "good"
      }
    ]
  }'
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

### Feature Importance
```bash
curl "http://localhost:8000/feature-importance?top_n=5"
```

## Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:8000"

# Single prediction
response = requests.post(
    f"{BASE_URL}/predict",
    json={
        "square_feet": 2500,
        "bedrooms": 4,
        "bathrooms": 2.5,
        "age": 10,
        "garage": 2,
        "location_score": 8.5,
        "condition": "good"
    }
)

print(response.json())
```

## Performance

- **Single Prediction**: ~50-100ms
- **Batch Prediction (100 items)**: ~500-1000ms
- **Model Info**: ~10ms
- **Feature Importance**: ~20ms

## Changelog

### Version 1.0.0 (2024-01-01)
- Initial release
- Single and batch prediction
- Model information endpoints
- Feature importance analysis
- Comprehensive error handling
- API documentation

## Support

For issues or questions:
1. Check the logs: `logs/app.log`
2. Review API documentation
3. Check health endpoint for status
4. Verify model files exist in `models/` directory

## Future Enhancements

- [ ] Batch processing with job IDs
- [ ] Webhook notifications
- [ ] Database integration
- [ ] Advanced filtering
- [ ] CSV export
- [ ] Model versioning
- [ ] A/B testing endpoints
- [ ] Performance analytics

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0
