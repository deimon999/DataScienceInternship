# Deployment & Advanced Setup Guide

## 📋 Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Model Retraining](#model-retraining)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Leave defaults if just testing
```

### Step 4: Generate Data

```bash
cd data
python generate_data.py --train-size 800 --test-size 200
cd ..
```

Expected output:
```
Training data saved: data/train.csv (800 samples)
Test data saved: data/test.csv (200 samples)
```

### Step 5: Train Models

```bash
python train.py
```

The training script will:
1. Load training data
2. Preprocess features
3. Train 5 different models
4. Evaluate on test set
5. Save best model and preprocessor

Expected training time: **2-5 minutes**

### Step 6: Run API Server

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: `http://localhost:8000`

### Step 7: Open Frontend

Option A: Open directly in browser
```
file:///path/to/Task-4-Full-DS-Project/frontend/index.html
```

Option B: Serve with Python
```bash
cd frontend
python -m http.server 8001
# Visit http://localhost:8001
```

### Step 8: Test the System

```bash
# Check health
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
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

---

## Docker Deployment

### Quickstart (Recommended)

```bash
# Build and run everything
docker-compose up --build

# Access:
# - API: http://localhost:8000
# - Dashboard: http://localhost
# - API Docs: http://localhost:8000/docs
```

### Step-by-Step

#### 1. Build Image

```bash
docker build -t house-price-prediction:latest .
```

#### 2. Run Container

```bash
docker run \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/logs:/app/logs \
  -e DEBUG=False \
  house-price-prediction:latest
```

#### 3. Verify

```bash
docker logs <container-id>
curl http://localhost:8000/health
```

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild after code changes
docker-compose up --build -d

# Execute command in container
docker-compose exec api python train.py
```

### Environment Variables in Docker

Edit `docker-compose.yml`:
```yaml
environment:
  - DEBUG=False
  - LOG_LEVEL=INFO
  - API_HOST=0.0.0.0
  - API_PORT=8000
```

---

## Production Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance

```bash
# Requirements: Ubuntu 20.04, t2.medium or larger
# Security Group: Allow ports 80, 8000

ssh -i your-key.pem ec2-user@your-instance-ip
```

#### 2. Install Docker & Docker Compose

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker
```

#### 3. Deploy Application

```bash
git clone <your-repo-url>
cd Task-4-Full-DS-Project

# Configure environment
cp .env.example .env
nano .env  # Edit for production

# Start services
docker-compose -f docker-compose.yml up -d

# Setup SSL (optional but recommended)
# Use Let's Encrypt with Certbot
```

#### 4. Setup Monitoring

```bash
# View logs
docker-compose logs -f api

# Monitor resources
docker stats

# Check API health
watch -n 5 'curl -s http://localhost:8000/health | python -m json.tool'
```

### Google Cloud Platform (Cloud Run)

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/house-price-prediction

# Deploy to Cloud Run
gcloud run deploy house-price-prediction \
  --image gcr.io/PROJECT_ID/house-price-prediction \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-house-price --location eastus

# Create App Service Plan
az appservice plan create \
  --name asp-house-price \
  --resource-group rg-house-price \
  --sku B1 --is-linux

# Deploy container
az webapp create \
  --resource-group rg-house-price \
  --plan asp-house-price \
  --name house-price-api \
  --deployment-container-image-name <image-url>
```

---

## Model Retraining

### Automated Retraining

```bash
# Add new training data to data/train.csv

# Retrain models
python train.py --train-path data/train.csv

# Restart API to load new models
docker-compose restart api
```

### Scheduled Retraining (Cron)

```bash
# Edit crontab
crontab -e

# Add daily retraining at 2 AM
0 2 * * * cd /path/to/Task-4-Full-DS-Project && python train.py
```

### Model Versioning

```bash
# Save with timestamp
cp models/best_model.pkl models/best_model_$(date +%Y%m%d_%H%M%S).pkl

# Keep history
ls -la models/best_model_*.pkl
```

---

## Monitoring & Logging

### View Logs

```bash
# Local
tail -f logs/app.log

# Docker
docker-compose logs -f api

# Follow specific pattern
tail -f logs/app.log | grep ERROR
```

### Log Analysis

```bash
# Count errors
grep ERROR logs/app.log | wc -l

# Parse JSON logs
cat logs/app.log | python -m json.tool | less

# Real-time monitoring
watch 'tail -20 logs/app.log'
```

### Performance Metrics

```bash
# Get metrics from logs
grep "Prediction made" logs/app.log | wc -l  # Total predictions

# Average response time
grep "RMSE" logs/app.log | tail -1  # Latest model RMSE
```

### Health Monitoring Script

```bash
#!/bin/bash
while true; do
  STATUS=$(curl -s http://localhost:8000/health)
  if echo $STATUS | grep -q "healthy"; then
    echo "✓ API Healthy at $(date)"
  else
    echo "✗ API Issue at $(date)"
    # Send alert
  fi
  sleep 300  # Check every 5 minutes
done
```

---

## Troubleshooting

### Models Won't Load

```bash
# Check if model files exist
ls -la models/

# Verify training completed
python train.py --train-path data/train.csv

# Check logs
tail -f logs/app.log | grep -i error
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Reduce batch size
# Edit config.py: reduce N_JOBS

# Restart container
docker-compose restart api
```

### API Slow

```bash
# Check server resources
docker stats

# Reduce feature count
# Edit config.py: N_FEATURES_TO_SELECT = 10

# Upgrade container resources
docker-compose down
# Edit docker-compose.yml: add resources limits
docker-compose up -d
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :8000
kill -9 <pid>
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps

# Verify connection string in .env
cat .env | grep DATABASE_URL

# Test connection
python -c "import sqlite3; sqlite3.connect(':memory:')"
```

### Frontend Not Connecting to API

1. Check API is running: `curl http://localhost:8000/health`
2. Check CORS settings in `src/api.py`
3. Update `API_BASE_URL` in `frontend/script.js`
4. Check browser console for errors (F12)

### Feature Mismatch After Retraining

```bash
# This happens if training data has different features
# Solution: Ensure data/train.csv has same columns

# Regenerate data
cd data
python generate_data.py
cd ..

# Retrain
python train.py
```

---

## Scaling Recommendations

### For 1K+ Daily Requests
- Upgrade to larger EC2 instance (t2.large)
- Add load balancing (AWS ELB)
- Implement caching (Redis)

### For 10K+ Daily Requests
- Use Kubernetes for auto-scaling
- Add API gateway with rate limiting
- Separate preprocessing to async jobs
- Use database for request logging

### For 100K+ Daily Requests
- Multi-region deployment
- Model serving (TensorFlow Serving)
- Distributed cache (Redis Cluster)
- Message queue (RabbitMQ, Kafka)

---

## Security Hardening

### Enable Authentication

```python
# In src/api.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/predict")
async def predict_single(data: HousePriceInput, credentials = Depends(security)):
    # Verify token
    return prediction
```

### Enable HTTPS

```bash
# Use nginx with SSL
# Update nginx.conf to redirect HTTP to HTTPS
```

### Rate Limiting

```bash
pip install slowapi

# Add to api.py
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## Performance Optimization

### Batch Inference

For large batches, the system already optimizes by:
- Using batch predictions endpoint
- Parallel preprocessing
- Vectorized numpy operations

### Model Optimization

To reduce latency:
1. Reduce feature count (SelectKBest)
2. Use simpler model (LightGBM)
3. Quantize model weights
4. Use ONNX format

---

## Backup & Recovery

### Backup Models

```bash
# Daily backup
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Upload to S3
aws s3 cp models_backup_*.tar.gz s3://your-bucket/backups/
```

### Recovery

```bash
# Restore from backup
tar -xzf models_backup_20240101.tar.gz

# Verify
python -c "from src.utils import load_model; load_model('models/best_model.pkl')"
```

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0
