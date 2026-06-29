# Credit Risk Scoring API

Production ML system for loan default prediction. Gradient Boosting classifier trained on Lending Club data with a React dashboard and FastAPI backend deployed on Vercel.

## Live Demo

**Dashboard:** [your-app.vercel.app](https://your-app.vercel.app)  
**API Docs:** [your-app.vercel.app/api/docs](https://your-app.vercel.app/api/docs)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Vercel Edge                     │
│                                                  │
│   React + Tailwind ──→ /api/predict ──→ Model   │
│   (Static Build)       (Python Serverless)       │
│                                                  │
│   Scaler: JSON params (no sklearn at runtime)    │
│   Model: Pickle + optional ONNX export           │
└─────────────────────────────────────────────────┘
```

## Model Performance

| Metric | Value |
|--------|-------|
| AUC-ROC | See `model/metrics.json` |
| Precision | See `model/metrics.json` |
| Recall | See `model/metrics.json` |
| F1 Score | See `model/metrics.json` |
| Cross-Val AUC | 5-fold with std |
| Training Data | Lending Club loan records |

> **Note:** Metrics above are from synthetic data used for CI. Train on [Lending Club data](https://www.kaggle.com/datasets/wordsforthewise/lending-club) for production metrics.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Predict default probability for a loan application |
| `GET` | `/api/health` | Health check and model status |
| `GET` | `/api/model-info` | Model metadata, metrics, and feature importances |
| `GET` | `/api/sample` | Sample loan applications for testing |
| `GET` | `/api/docs` | Interactive Swagger documentation |

### Prediction Request

```json
{
  "loan_amnt": 15000,
  "int_rate": 12.5,
  "annual_inc": 60000,
  "dti": 18.5,
  "delinq_2yrs": 0,
  "inq_last_6mths": 1,
  "open_acc": 8,
  "revol_util": 45.0,
  "total_acc": 15,
  "emp_length": 3
}
```

### Prediction Response

```json
{
  "default_probability": 0.1823,
  "risk_tier": "MODERATE",
  "risk_score": 685,
  "recommendation": "Approve — review pricing",
  "confidence": "High",
  "feature_importance": {
    "int_rate": 0.2847,
    "dti": 0.1923,
    "revol_util": 0.1456,
    "annual_inc": 0.1203,
    "delinq_2yrs": 0.0891
  },
  "input_summary": {
    "loan_amount": 15000,
    "interest_rate": 12.5,
    "annual_income": 60000,
    "dti_ratio": 18.5
  }
}
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Setup

```bash
# Clone
git clone https://github.com/Gaze31/credit-risk-api.git
cd credit-risk-api

# Install Python dependencies
pip install -r requirements-dev.txt

# Train model (synthetic data for development)
python training/train_model.py --synthetic

# Train model (real Lending Club data)
# Download from: https://www.kaggle.com/datasets/wordsforthewise/lending-club
python training/train_model.py --data training/data/accepted_2007_to_2018Q4.csv

# Start API
uvicorn api.index:app --reload --port 8000

# Install frontend dependencies
npm install

# Start frontend dev server
npm run dev
```

### Run Tests

```bash
pytest tests/ -v
```

## Deployment (Vercel)

1. Push to GitHub
2. Import repo in [Vercel](https://vercel.com)
3. Deploy — Vercel auto-detects the config from `vercel.json`

The frontend builds as static files. The API runs as a Python serverless function. Scaler parameters are stored as JSON so no scikit-learn is needed at inference time for scaling — only for the model pickle.

## Tech Stack

**Backend:** Python, FastAPI, scikit-learn, Gradient Boosting, Pydantic, NumPy  
**Frontend:** React 18, Tailwind CSS, Recharts, Lucide Icons, Vite  
**Deployment:** Vercel (static + serverless), GitHub Actions CI  
**ML Pipeline:** StandardScaler (JSON export), cross-validation, calibration analysis

## Project Structure

```
credit-risk-api/
├── api/
│   └── index.py              # FastAPI serverless endpoint
├── src/
│   ├── components/
│   │   ├── Header.jsx         # App header with health status
│   │   ├── LoanForm.jsx       # Loan application input form
│   │   ├── RiskResult.jsx     # Risk assessment results + charts
│   │   ├── PredictionHistory.jsx  # Prediction log table
│   │   └── ModelMetrics.jsx   # Model performance dashboard
│   ├── App.jsx                # Main application
│   ├── main.jsx               # Entry point
│   └── index.css              # Tailwind imports
├── training/
│   └── train_model.py         # Training pipeline (LC data + synthetic)
├── model/                     # Trained model artifacts
│   ├── credit_model.pkl       # Gradient Boosting model
│   ├── scaler.json            # StandardScaler params (JSON)
│   ├── features.json          # Feature list
│   ├── metrics.json           # Evaluation metrics
│   └── metadata.json          # Model metadata
├── tests/
│   ├── test_api.py            # 21 API tests
│   └── test_training.py       # 10 training pipeline tests
├── .github/workflows/
│   └── ci.yml                 # GitHub Actions CI
├── vercel.json                # Vercel deployment config
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── package.json               # Frontend dependencies
```

## License

MIT
