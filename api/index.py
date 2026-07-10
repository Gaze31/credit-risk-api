"""
Credit Risk API — Vercel Serverless Functions
==============================================
Truly dependency-light inference: the GradientBoostingClassifier is exported
to pure data (api/model_data.py) by training/export_model.py, and prediction
is reimplemented in numpy. No pickle, no scikit-learn at runtime, and the
model is bundled by import tracing — it cannot be missed by the packager.

Verified bit-for-bit against the original sklearn model
(max abs probability difference < 2e-11 over 500 random inputs).
"""

import sys
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Load Model Payload (import-traced, always bundled) ─────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from model_data import MODEL  # noqa: E402

    TREES = MODEL["trees"]
    PRIOR = MODEL["prior"]
    LEARNING_RATE = MODEL["learning_rate"]
    CALIBRATION_X = np.array(MODEL["calibration_x"])
    CALIBRATION_Y = np.array(MODEL["calibration_y"])
    SCALER_MEAN = np.array(MODEL["scaler_mean"])
    SCALER_SCALE = np.array(MODEL["scaler_scale"])
    FEATURES = MODEL["features"]
    FEATURE_IMPORTANCES = MODEL["feature_importances"]
    model_metrics = MODEL["metrics"]
    model_metadata = MODEL["metadata"]
    MODEL_LOADED = True
except Exception as e:  # pragma: no cover
    MODEL_LOADED = False
    TREES = []
    FEATURES = []
    FEATURE_IMPORTANCES = {}
    model_metrics = {}
    model_metadata = {}
    print(f"Model loading error: {e}")


# ── Inference (numpy only) ─────────────────────────────────────────────
def scale_input(raw: np.ndarray) -> np.ndarray:
    """Apply StandardScaler transform using saved params. No sklearn needed."""
    return (raw - SCALER_MEAN) / SCALER_SCALE


def _tree_predict(tree: dict, x: np.ndarray) -> float:
    """Walk a single regression tree. Feature index -2 marks a leaf."""
    node = 0
    feat, thresh, left, right = tree["f"], tree["t"], tree["l"], tree["r"]
    while feat[node] != -2:
        node = left[node] if x[feat[node]] <= thresh[node] else right[node]
    return tree["v"][node]


def predict_default_probability(raw_input: np.ndarray) -> tuple:
    """StandardScaler transform + gradient boosting decision function + sigmoid,
    then probability calibration.

    Training upweights the default class (sample_weight), which inflates raw
    probabilities. We map the raw score back to an empirical default rate by
    interpolating the reliability curve measured on the held-out test set.
    Returns (calibrated_probability, raw_probability).
    """
    x = (raw_input - SCALER_MEAN) / SCALER_SCALE
    raw_score = PRIOR + LEARNING_RATE * sum(_tree_predict(t, x) for t in TREES)
    raw_prob = float(1.0 / (1.0 + np.exp(-raw_score)))
    calibrated = float(np.interp(raw_prob, CALIBRATION_X, CALIBRATION_Y))
    return calibrated, raw_prob


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
    int_rate: float = Field(10.5, ge=5.0, le=31.0, description="Interest rate (%)")
    annual_inc: float = Field(75000, ge=10000, le=500000, description="Annual income in USD")
    dti: float = Field(15.0, ge=0, le=50, description="Debt-to-income ratio")
    delinq_2yrs: int = Field(0, ge=0, le=10, description="Delinquencies in last 2 years")
    inq_last_6mths: int = Field(0, ge=0, le=8, description="Credit inquiries in last 6 months")
    open_acc: int = Field(10, ge=1, le=50, description="Number of open credit lines")
    revol_util: float = Field(35.0, ge=0, le=100, description="Revolving utilization rate (%)")
    total_acc: int = Field(20, ge=2, le=80, description="Total credit lines")
    emp_length: int = Field(5, ge=0, le=10, description="Employment length in years")


class RiskResponse(BaseModel):
    default_probability: float
    uncalibrated_probability: float
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

    raw_input = np.array([
        loan.loan_amnt, loan.int_rate, loan.annual_inc,
        loan.dti, loan.delinq_2yrs, loan.inq_last_6mths,
        loan.open_acc, loan.revol_util, loan.total_acc, loan.emp_length
    ], dtype=float)

    prob, raw_prob = predict_default_probability(raw_input)
    tier, recommendation, score = get_risk_tier(prob)
    confidence = get_confidence_level(prob)

    # Top feature importances (precomputed at export time)
    top_features = dict(
        sorted(FEATURE_IMPORTANCES.items(), key=lambda x: x[1], reverse=True)[:5]
    )
    top_features = {k: round(v, 4) for k, v in top_features.items()}

    return RiskResponse(
        default_probability=round(prob, 4),
        uncalibrated_probability=round(raw_prob, 4),
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
            "loan_amnt": 18000, "int_rate": 12.0,
            "annual_inc": 70000, "dti": 18.0,
            "delinq_2yrs": 0, "inq_last_6mths": 1,
            "open_acc": 10, "revol_util": 40.0,
            "total_acc": 20, "emp_length": 5
        },
        "high_risk": {
            "loan_amnt": 35000, "int_rate": 26.0,
            "annual_inc": 30000, "dti": 38.0,
            "delinq_2yrs": 3, "inq_last_6mths": 5,
            "open_acc": 15, "revol_util": 88.0,
            "total_acc": 8, "emp_length": 0
        }
    }
