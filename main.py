from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np

# Load model
with open("model/credit_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("model/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("model/features.pkl", "rb") as f:
    features = pickle.load(f)

app = FastAPI(
    title="Credit Risk API",
    description="ML-powered loan default prediction | AUC-ROC: 0.897",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoanApplication(BaseModel):
    loan_amnt: float = 15000
    int_rate: float = 12.5
    annual_inc: float = 60000
    dti: float = 18.5
    delinq_2yrs: int = 0
    inq_last_6mths: int = 1
    open_acc: int = 8
    revol_util: float = 45.0
    total_acc: int = 15
    emp_length: int = 3

class RiskResponse(BaseModel):
    default_probability: float
    risk_tier: str
    risk_score: int
    recommendation: str
    feature_importance: dict

def get_risk_tier(prob: float):
    if prob < 0.15:
        return "LOW", "Approve", 850 - int(prob * 300)
    elif prob < 0.30:
        return "MEDIUM", "Review manually", 700 - int(prob * 200)
    elif prob < 0.50:
        return "HIGH", "Additional verification required", 600 - int(prob * 150)
    else:
        return "VERY HIGH", "Decline", 500 - int(prob * 100)

@app.get("/")
def root():
    return {
        "api": "Credit Risk Scoring API",
        "version": "1.0.0",
        "model": "Gradient Boosting | AUC-ROC: 0.897",
        "endpoints": ["/predict", "/health", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict", response_model=RiskResponse)
def predict(loan: LoanApplication):
    input_data = [[
        loan.loan_amnt, loan.int_rate, loan.annual_inc,
        loan.dti, loan.delinq_2yrs, loan.inq_last_6mths,
        loan.open_acc, loan.revol_util, loan.total_acc, loan.emp_length
    ]]

    scaled = scaler.transform(input_data)
    prob = model.predict_proba(scaled)[0][1]
    tier, recommendation, score = get_risk_tier(prob)

    importances = dict(zip(features, model.feature_importances_))
    top3 = dict(sorted(importances.items(),
                key=lambda x: x[1], reverse=True)[:3])

    return RiskResponse(
        default_probability=round(float(prob), 4),
        risk_tier=tier,
        risk_score=max(300, min(850, score)),
        recommendation=recommendation,
        feature_importance=top3
    )

@app.get("/sample")
def sample_applications():
    return {
        "low_risk": {
            "loan_amnt": 10000, "int_rate": 7.5,
            "annual_inc": 90000, "dti": 8.0,
            "delinq_2yrs": 0, "inq_last_6mths": 0,
            "open_acc": 10, "revol_util": 20.0,
            "total_acc": 20, "emp_length": 8
        },
        "high_risk": {
            "loan_amnt": 35000, "int_rate": 28.0,
            "annual_inc": 25000, "dti": 38.0,
            "delinq_2yrs": 3, "inq_last_6mths": 5,
            "open_acc": 15, "revol_util": 92.0,
            "total_acc": 8, "emp_length": 0
        }
    }
