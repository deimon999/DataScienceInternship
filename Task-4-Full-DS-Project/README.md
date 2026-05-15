# House Price Prediction - Full End-to-End Data Science Project

## 🏠 Project Overview

A **production-ready, advanced end-to-end data science project** that demonstrates modern ML practices from data collection to deployment. The system predicts house prices using an ensemble of machine learning models and provides both a RESTful API and an interactive web dashboard.

### Key Features
✅ **Advanced Data Pipeline** - Preprocessing, feature engineering, outlier detection  
✅ **Ensemble ML Models** - XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting  
✅ **FastAPI Backend** - Production-ready REST API with comprehensive endpoints  
✅ **Modern Web Dashboard** - Responsive frontend with real-time predictions  
✅ **Docker Support** - Easy deployment with Docker & Docker Compose  
✅ **Comprehensive Testing** - Unit and integration tests  
✅ **Logging & Monitoring** - Structured logging with JSON format  
✅ **Advanced Features** - Data drift detection, feature importance, model evaluation  

## 📁 Project Structure

```
Task-4-Full-DS-Project/
├── data/
│   ├── generate_data.py          # Synthetic dataset generation
│   ├── train.csv                 # Training data
│   └── test.csv                  # Test data
│
├── src/
│   ├── api.py                    # FastAPI application
│   ├── config.py                 # Configuration management
│   ├── data_pipeline.py          # Advanced preprocessing & feature engineering
│   ├── model_training.py         # Model training & ensemble
│   ├── logger_setup.py           # Logging configuration
│   └── utils.py                  # Utility functions
│
├── frontend/
│   ├── index.html                # Dashboard UI
│   ├── styles.css                # Modern styling
│   └── script.js                 # Frontend logic
│
├── models/                       # Trained model artifacts
│   ├── best_model.pkl
│   ├── preprocessor.pkl
│   └── scaler.pkl
│
├── tests/
│   ├── test_core.py              # Unit tests
│   └── test_api.py               # API integration tests
│
├── train.py                      # Training script
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose setup
├── nginx.conf                    # Nginx configuration
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🚀 Quick Start

### Option 1: Local Development

#### 1. Create Python Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Generate Dataset
```bash
cd data
python generate_data.py --train-size 800 --test-size 200 --output-dir .
cd ..
```

#### 4. Train Models
```bash
python train.py --train-path data/train.csv --test-path data/test.csv
```

#### 5. Start API Server
```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

#### 6. Access Dashboard
Open `frontend/index.html` in your browser or serve it with a simple HTTP server:
```bash
cd frontend
python -m http.server 8001
# Visit http://localhost:8001
```

### Option 2: Docker Deployment

#### 1. Build and Run with Docker Compose
```bash
docker-compose up --build
```

Access:
- **API**: http://localhost:8000
- **Dashboard**: http://localhost
- **API Docs**: http://localhost:8000/docs

#### 2. Custom Docker Build
```bash
docker build -t house-price-prediction .
docker run -p 8000:8000 -v $(pwd)/models:/app/models house-price-prediction
```

## 📊 API Endpoints

### Health & Status
```
GET /health
GET /
```

### Predictions
```
POST /predict
POST /batch-predict
```

### Model Information
```
GET /model-info
GET /feature-importance?top_n=10
```

### Example Prediction Request
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

## 🔧 Configuration

Edit `.env` to customize:
```bash
cp .env.example .env
```

Key Settings:
- `API_HOST` & `API_PORT` - API server configuration
- `FEATURE_SCALING` - Scaler type (standard, robust, minmax)
- `MISSING_VALUE_STRATEGY` - Imputation method (median, mean)
- Model hyperparameters in `src/config.py`

## 🎯 Advanced Features

### 1. Advanced Data Pipeline
- **Automatic feature type detection**
- **Smart missing value imputation**
- **Outlier detection & handling** (IQR and Z-score methods)
- **Advanced feature engineering** (polynomial, interactions)
- **Automatic feature selection** (SelectKBest)
- **Multiple scaling options** (StandardScaler, RobustScaler, MinMaxScaler)

### 2. Ensemble Learning
- **5 different models** trained in parallel
- **Cross-validation** for robust evaluation
- **Automatic best model selection**
- **Feature importance analysis**

### 3. Production-Ready API
- **Input validation** with Pydantic
- **Error handling** with proper HTTP codes
- **CORS support** for cross-domain requests
- **Comprehensive logging**
- **Async endpoints** for better performance
- **API documentation** (Swagger/OpenAPI)

### 4. Dashboard Features
- **Single prediction interface**
- **Batch CSV processing**
- **Real-time API status**
- **Model information display**
- **Prediction analytics**
- **Responsive design** (mobile-friendly)

### 5. Monitoring & Logging
- **Structured JSON logging**
- **Performance metrics**
- **Data drift detection**
- **Model evaluation reports**

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Tests
```bash
pytest tests/test_core.py -v
pytest tests/test_api.py -v
```

### Test Coverage
```bash
pytest --cov=src tests/
```

## 📈 Model Performance

The ensemble includes:
- **XGBoost** - Gradient boosting excellence
- **LightGBM** - Fast and memory-efficient
- **CatBoost** - Categorical feature handling
- **Random Forest** - Interpretability
- **Gradient Boosting** - Robust predictions

Each model is trained with cross-validation (5-fold) and the best performer is selected for inference.

## 📚 Data Format

### Input Features
| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| square_feet | int | 500-5000 | House size |
| bedrooms | int | 1-10 | Number of bedrooms |
| bathrooms | float | 1-10 | Number of bathrooms |
| age | int | 0-150 | Years old |
| garage | int | 0-5 | Garage spaces |
| location_score | float | 1-10 | Location desirability |
| condition | str | excellent/good/fair/poor | House condition |

### Output
- **predicted_price** - Estimated house price
- **confidence** - Model confidence level (0-1)
- **prediction_range** - Price range (±10%)

## 🔐 Security Considerations

- Input validation on all endpoints
- SQL injection prevention (no SQL used)
- CORS properly configured
- Environment variables for sensitive data
- No hardcoded credentials
- Proper error messages without system details

## 📝 Logging

Logs are stored in `logs/app.log` with:
- **JSON format** for easy parsing
- **Timestamp** for tracking
- **Log levels** (INFO, WARNING, ERROR)
- **Structured data** for analysis

## 🚀 Deployment Strategies

### 1. Local Development
Use `python -m uvicorn` with `--reload` flag

### 2. Docker
```bash
docker-compose up -d
```

### 3. Kubernetes
- Create deployment YAML
- Use ConfigMaps for configuration
- Implement health checks

### 4. Cloud Platforms
- **AWS**: EC2 + RDS
- **GCP**: Cloud Run or App Engine
- **Azure**: App Service

## 🔄 Workflow

1. **Data Generation** → Generate synthetic house price data
2. **Preprocessing** → Clean, transform, engineer features
3. **Model Training** → Train ensemble of models
4. **Evaluation** → Cross-validate and test
5. **Deployment** → Serve via API
6. **Monitoring** → Track performance and drift

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ End-to-end ML pipeline development
- ✅ Advanced preprocessing techniques
- ✅ Ensemble learning methods
- ✅ REST API design & development
- ✅ Frontend integration
- ✅ Docker containerization
- ✅ Testing & CI/CD practices
- ✅ Production-ready code quality
- ✅ Logging & monitoring
- ✅ Modern web development

## 📦 Dependencies

- **Data Processing**: pandas, numpy, scikit-learn
- **ML Models**: xgboost, lightgbm, catboost, tensorflow
- **API Framework**: fastapi, uvicorn, pydantic
- **Testing**: pytest, pytest-asyncio
- **Logging**: python-json-logger
- **Utilities**: joblib, python-dotenv

See `requirements.txt` for complete list.

## 🤝 Contributing

To extend this project:
1. Add new models to `ModelTrainer`
2. Create custom features in `AdvancedPreprocessor`
3. Add new API endpoints in `api.py`
4. Update frontend with new visualizations
5. Write tests for new features

## 📄 License

This project is part of CODTECH Internship program.

## 🎯 Future Enhancements

- [ ] Real estate API integration for live data
- [ ] Advanced visualization dashboard
- [ ] A/B testing framework
- [ ] Model retraining pipeline
- [ ] Database integration (PostgreSQL)
- [ ] Kubernetes deployment
- [ ] Model serving (TensorFlow Serving)
- [ ] Real-time monitoring
- [ ] Feature store implementation
- [ ] Explainable AI (SHAP values)

## ❓ FAQ

**Q: How do I update the API URL in the frontend?**
A: Change `API_BASE_URL` in `frontend/script.js`

**Q: Can I use real data instead of synthetic?**
A: Yes! Update `data/train.csv` and `data/test.csv`, then retrain.

**Q: How do I add new features?**
A: Add them to the CSV and update `HousePriceInput` model in `api.py`

**Q: Is this production-ready?**
A: Yes! It includes error handling, logging, testing, and Docker support.

---

**Built with ❤️ for CODTECH Internship**  
**End-to-End Data Science Excellence**
