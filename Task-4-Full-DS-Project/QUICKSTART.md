# QUICKSTART GUIDE - House Price Prediction System

## ⚡ 5-Minute Quick Start

### Option 1: Using Docker (Easiest)

```bash
# One command to run everything!
docker-compose up --build

# Wait for startup... then open:
# Dashboard: http://localhost
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**That's it!** The system is ready to use.

---

### Option 2: Local Python (Recommended for Development)

#### Step 1: Setup (1 minute)
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Prepare Data (30 seconds)
```bash
cd data
python generate_data.py
cd ..
```

#### Step 3: Train Models (3 minutes)
```bash
python train.py
```

Watch as it trains:
- XGBoost ✓
- LightGBM ✓
- CatBoost ✓
- Random Forest ✓
- Gradient Boosting ✓

#### Step 4: Start API (30 seconds)
```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 5: Open Dashboard
- **Option A**: Open `frontend/index.html` in your browser
- **Option B**: Serve locally
```bash
cd frontend
python -m http.server 8001
# Visit http://localhost:8001
```

---

## 🧪 Test It Out

### Quick Prediction

Open your terminal and run:

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

Expected response:
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

### Check Health
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit: http://localhost:8000/docs

---

## 📊 What You Get

✅ **Advanced ML Models** - Trained ensemble of 5 different models  
✅ **Production API** - FastAPI with comprehensive endpoints  
✅ **Modern Dashboard** - Beautiful, responsive web interface  
✅ **Batch Processing** - Upload CSV for bulk predictions  
✅ **Model Info** - Feature importance, metrics, and more  
✅ **Full Documentation** - API docs, deployment guides  
✅ **Docker Ready** - One-command deployment  
✅ **Testing Suite** - Unit and integration tests  

---

## 📁 Project Structure Overview

```
Task-4-Full-DS-Project/
├── src/                    # Core Python modules
├── frontend/               # Web dashboard (HTML/CSS/JS)
├── data/                   # Datasets and data generation
├── models/                 # Trained model artifacts
├── tests/                  # Unit and integration tests
├── train.py               # Model training script
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker setup
└── README.md             # Full documentation
```

---

## 🔑 Key Files to Know

| File | Purpose |
|------|---------|
| `train.py` | Main training pipeline |
| `src/api.py` | FastAPI REST API |
| `src/data_pipeline.py` | Data preprocessing & features |
| `src/model_training.py` | Model ensemble & training |
| `frontend/index.html` | Dashboard interface |
| `frontend/script.js` | Frontend API calls |
| `requirements.txt` | All dependencies |

---

## 💡 Common Tasks

### Make a Prediction
1. Open dashboard: `frontend/index.html`
2. Enter house features
3. Click "Predict Price"
4. View results with confidence & range

### Batch Predict (Multiple Houses)
1. Open "Batch Prediction" tab
2. Upload CSV file with house data
3. View results table and statistics

### See Model Performance
1. Open "Model Info" tab
2. View trained model type
3. See top 10 important features
4. Check feature importance scores

### Check System Status
```bash
curl http://localhost:8000/health
```

---

## 🚀 Next Steps

### Want More Features?
See `README.md` for advanced features like:
- Data drift detection
- Logging and monitoring
- Deployment strategies
- Scaling recommendations

### Want to Deploy?
See `DEPLOYMENT.md` for:
- AWS EC2 setup
- Google Cloud deployment
- Azure App Service
- Kubernetes
- Production hardening

### Want API Details?
See `API.md` for:
- All endpoints
- Request/response formats
- Error handling
- Code examples

---

## ⚠️ Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the project root
cd Task-4-Full-DS-Project

# Reinstall dependencies
pip install -r requirements.txt
```

### API won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
python -m uvicorn src.api:app --port 9000
```

### Models not found
```bash
# Train models first
python train.py

# Check they exist
ls models/
```

### Frontend can't reach API
1. Make sure API is running: `curl http://localhost:8000/health`
2. Edit `frontend/script.js` and set correct `API_BASE_URL`
3. Check browser console for CORS errors (F12)

---

## 📞 Quick Reference

### URLs
- **Dashboard**: `frontend/index.html` or `http://localhost`
- **API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

### Commands
```bash
# Generate data
python data/generate_data.py

# Train models
python train.py

# Run API
python -m uvicorn src.api:app --reload

# Run tests
pytest tests/

# Docker commands
docker-compose up
docker-compose down
docker-compose logs -f api
```

### Environment
- Edit `.env` for configuration
- Default settings work out of the box
- See `.env.example` for all options

---

## 🎓 Learning Path

1. **Start Here** → Run `docker-compose up` or local setup
2. **Try Predictions** → Use dashboard to make predictions
3. **Check Code** → Review `src/api.py` and `src/data_pipeline.py`
4. **Customize** → Add new features or models
5. **Deploy** → Use Docker and DEPLOYMENT.md guide

---

## 📚 Documentation Files

- **README.md** - Full project documentation
- **API.md** - Complete API reference
- **DEPLOYMENT.md** - Production deployment guide
- **QUICKSTART.md** - This file

---

## ✨ Features Included

### Data Processing
- Automatic feature type detection
- Smart missing value handling
- Outlier detection & removal
- Advanced feature engineering
- Automatic feature selection
- Multiple scaling options

### Machine Learning
- 5 ensemble models
- Cross-validation
- Automatic best model selection
- Feature importance analysis
- Performance metrics

### API
- RESTful endpoints
- Input validation
- Error handling
- CORS support
- Async operations
- Auto-generated docs

### Frontend
- Single predictions
- Batch processing
- Model information
- Analytics dashboard
- Real-time API status
- Responsive design

---

## 🎯 Success Checklist

After setup, verify:
- [ ] `python train.py` completes successfully
- [ ] `http://localhost:8000/health` returns {"status": "healthy"}
- [ ] Dashboard loads at `frontend/index.html`
- [ ] Can make prediction in dashboard
- [ ] API documentation visible at `/docs`

---

## 📞 Need Help?

1. Check logs: `tail -f logs/app.log`
2. Review README.md for full docs
3. Check DEPLOYMENT.md for advanced setup
4. Review API.md for endpoint details
5. Check test files for usage examples

---

**Ready? Start with:** `docker-compose up --build`

**Enjoy your advanced ML system!** 🚀

---

Last Updated: 2024-01-01
