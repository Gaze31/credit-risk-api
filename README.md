# Credit Risk Scoring API

Production-ready REST API for ML-powered loan default prediction.

## Model Performance
- AUC-ROC: 0.897
- Algorithm: Gradient Boosting Classifier
- Training data: 32,574 loan records

## API Endpoints
- GET / — API info
- GET /health — health check
- POST /predict — predict default probability
- GET /sample — sample loan applications
- GET /docs — interactive Swagger UI

## Quick Start
pip install -r requirements.txt
python train_model.py
uvicorn main:app --reload

## Response Example
{
  "default_probability": 0.0823,
  "risk_tier": "LOW",
  "risk_score": 812,
  "recommendation": "Approve",
  "feature_importance": {"int_rate": 0.31, "dti": 0.22, "revol_util": 0.18}
}

## Tech Stack
Python · FastAPI · scikit-learn · Gradient Boosting · Pydantic · uvicorn
