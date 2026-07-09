"""
Credit Risk API — Vercel Serverless Functions
==============================================
Lightweight inference endpoint using pickle model + JSON scaler.
No scikit-learn needed at runtime — just numpy for scaling + prediction.
"""

import json
import os
import pickle
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = next((p for p in [Path(__file__).resolve().parent / "model", BASE_DIR / "model"] if (p / "credit_model.pkl").exists()), Path(__file__).resolve().parent / "model")

# ── Load Artifacts ─────────────────────────────────────────────────────
try:
    with open(MODEL_DIR / "credit_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open(MODEL_DIR / "scaler.json", "r") as f:
        scaler_params = json.load(f)

    with open(MODEL_DIR / "features.json", "r") as f:
        FEATURES = json.load(f)

    with open(MODEL_DIR / "metrics.json", "r") as f:
        model_metrics = json.load(f)

    with open(MODEL_DIR / "metadata.json", "r") as f:
        model_metadata = json.load(f)

    SCALER_MEAN = np.array(scaler_params["mean"])
    SCALER_SCALE = np.array(scaler_params["scale"])
    MODEL_LOADED = True
except Exception as e:
    MODEL_LOADED = False
    model = None
    FEATURES = []
    model_metrics = {}
    model_metadata = {}
    print(f"Model loading error: {e}")

# ── FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Credit Risk Scoring API",
    description=(
        "ML-powered loan default prediction using Gradient Boosting "
        "trained on Lending Club data. Returns risk tier, credit score, "
        "default probability, and feature importances."
    ),
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ──────────────────────────────────────────
class LoanApplication(BaseModel):
    loan_amnt: float = Field(15000, ge=500, le=40000, description="Loan amount in USD")
    int_rate: float = Field(12.5, ge=5.0, le=31.0, description="Interest rate (%)")
    annual_inc: float = Field(60000, ge=10000, le=500000, description="Annual income in USD")
    dti: float = Field(18.5, ge=0, le=50, description="Debt-to-income ratio")
    delinq_2yrs: int = Field(0, ge=0, le=10, description="Delinquencies in last 2 years")
    inq_last_6mths: int = Field(1, ge=0, le=8, description="Credit inquiries in last 6 months")
    open_acc: int = Field(8, ge=1, le=50, description="Number of open credit lines")
    revol_util: float = Field(45.0, ge=0, le=100, description="Revolving utilization rate (%)")
    total_acc: int = Field(15, ge=2, le=80, description="Total credit lines")
    emp_length: int = Field(3, ge=0, le=10, description="Employment length in years")


class RiskResponse(BaseModel):
    default_probability: float
    risk_tier: str
    risk_score: int
    recommendation: str
    confidence: str
    feature_importance: dict
    input_summary: dict


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: str
    version: str


class ModelInfoResponse(BaseModel):
    model_type: str
    features: list
    metrics: dict
    training_info: dict


# ── Helper Functions ───────────────────────────────────────────────────
def scale_input(raw: np.ndarray) -> np.ndarray:
    """Apply StandardScaler transform using saved params. No sklearn needed."""
    return (raw - SCALER_MEAN) / SCALER_SCALE


def get_risk_tier(prob: float) -> tuple:
    """Map default probability to risk tier, recommendation, and score."""
    if prob < 0.10:
        return "LOW", "Approve — standard terms", int(820 - prob * 200)
    elif prob < 0.20:
        return "MODERATE", "Approve — review pricing", int(740 - prob * 300)
    elif prob < 0.35:
        return "HIGH", "Manual review required", int(650 - prob * 200)
    elif prob < 0.50:
        return "VERY HIGH", "Additional collateral required", int(550 - prob * 150)
    else:
        return "CRITICAL", "Decline — excessive default risk", int(450 - prob * 100)


def get_confidence_level(prob: float) -> str:
    """Assess prediction confidence based on probability distance from 0.5."""
    distance = abs(prob - 0.5)
    if distance > 0.35:
        return "Very High"
    elif distance > 0.25:
        return "High"
    elif distance > 0.15:
        return "Moderate"
    else:
        return "Low — near decision boundary"


# ── Endpoints ──────────────────────────────────────────────────────────
@app.get("/api")
def root():
    return {
        "api": "Credit Risk Scoring API",
        "version": "2.0.0",
        "model": f"{model_metadata.get('model_type', 'N/A')} | AUC-ROC: {model_metrics.get('auc_roc', 'N/A')}",
        "endpoints": {
            "predict": "POST /api/predict",
            "health": "GET /api/health",
            "model_info": "GET /api/model-info",
            "sample": "GET /api/sample",
            "docs": "GET /api/docs"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="healthy" if MODEL_LOADED else "degraded",
        model_loaded=MODEL_LOADED,
        model_type=model_metadata.get("model_type", "unknown"),
        version="2.0.0"
    )


@app.post("/api/predict", response_model=RiskResponse)
def predict(loan: LoanApplication):
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded")

    raw_input = np.array([[
        loan.loan_amnt, loan.int_rate, loan.annual_inc,
        loan.dti, loan.delinq_2yrs, loan.inq_last_6mths,
        loan.open_acc, loan.revol_util, loan.total_acc, loan.emp_length
    ]])

    scaled = scale_input(raw_input)
    prob = float(model.predict_proba(scaled)[0][1])
    tier, recommendation, score = get_risk_tier(prob)
    confidence = get_confidence_level(prob)

    # Feature importances
    importances = dict(zip(FEATURES, model.feature_importances_.tolist()))
    top_features = dict(
        sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
    )
    # Round for readability
    top_features = {k: round(v, 4) for k, v in top_features.items()}

    return RiskResponse(
        default_probability=round(prob, 4),
        risk_tier=tier,
        risk_score=max(300, min(850, score)),
        recommendation=recommendation,
        confidence=confidence,
        feature_importance=top_features,
        input_summary={
            "loan_amount": loan.loan_amnt,
            "interest_rate": loan.int_rate,
            "annual_income": loan.annual_inc,
            "dti_ratio": loan.dti
        }
    )


@app.get("/api/model-info", response_model=ModelInfoResponse)
def model_info():
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return ModelInfoResponse(
        model_type=model_metadata.get("model_type", "unknown"),
        features=FEATURES,
        metrics={
            "auc_roc": model_metrics.get("auc_roc"),
            "precision": model_metrics.get("precision"),
            "recall": model_metrics.get("recall"),
            "f1_score": model_metrics.get("f1_score"),
            "cv_auc_mean": model_metrics.get("cv_auc_mean"),
            "cv_auc_std": model_metrics.get("cv_auc_std"),
        },
        training_info={
            "train_size": model_metrics.get("train_size"),
            "test_size": model_metrics.get("test_size"),
            "default_rate": model_metrics.get("default_rate"),
            "confusion_matrix": model_metrics.get("confusion_matrix"),
            "feature_importances": model_metrics.get("feature_importances"),
        }
    )


@app.get("/api/sample")
def sample_applications():
    return {
        "low_risk": {
            "loan_amnt": 10000, "int_rate": 7.5,
            "annual_inc": 95000, "dti": 8.0,
            "delinq_2yrs": 0, "inq_last_6mths": 0,
            "open_acc": 12, "revol_util": 18.0,
            "total_acc": 25, "emp_length": 8
        },
        "moderate_risk": {
            "loan_amnt": 20000, "int_rate": 15.0,
            "annual_inc": 55000, "dti": 22.0,
            "delinq_2yrs": 1, "inq_last_6mths": 2,
            "open_acc": 8, "revol_util": 55.0,
            "total_acc": 15, "emp_length": 3
        },
        "high_risk": {
            "loan_amnt": 35000, "int_rate": 26.0,
            "annual_inc": 30000, "dti": 38.0,
            "delinq_2yrs": 3, "inq_last_6mths": 5,
            "open_acc": 15, "revol_util": 88.0,
            "total_acc": 8, "emp_length": 0
        }
    }
