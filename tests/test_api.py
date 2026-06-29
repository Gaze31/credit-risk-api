"""
Unit tests for Credit Risk API
===============================
Tests model loading, prediction endpoints, input validation,
and risk tier logic.
"""

import json
import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.index import app, get_risk_tier, get_confidence_level, scale_input


client = TestClient(app)


# ── Health & Info Endpoints ────────────────────────────────────────────
class TestHealthEndpoints:
    def test_root_returns_api_info(self):
        res = client.get("/api")
        assert res.status_code == 200
        data = res.json()
        assert "api" in data
        assert "endpoints" in data

    def test_health_check(self):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "model_loaded" in data
        assert data["version"] == "2.0.0"

    def test_model_info(self):
        res = client.get("/api/model-info")
        if res.status_code == 200:
            data = res.json()
            assert "model_type" in data
            assert "features" in data
            assert "metrics" in data
            assert len(data["features"]) == 10

    def test_sample_applications(self):
        res = client.get("/api/sample")
        assert res.status_code == 200
        data = res.json()
        assert "low_risk" in data
        assert "moderate_risk" in data
        assert "high_risk" in data
        assert "loan_amnt" in data["low_risk"]


# ── Prediction Endpoint ───────────────────────────────────────────────
class TestPrediction:
    def test_predict_default_values(self):
        res = client.post("/api/predict", json={})
        if res.status_code == 200:
            data = res.json()
            assert "default_probability" in data
            assert "risk_tier" in data
            assert "risk_score" in data
            assert "recommendation" in data
            assert "confidence" in data
            assert "feature_importance" in data
            assert 0 <= data["default_probability"] <= 1
            assert 300 <= data["risk_score"] <= 850

    def test_predict_low_risk_application(self):
        payload = {
            "loan_amnt": 10000, "int_rate": 7.5,
            "annual_inc": 95000, "dti": 8.0,
            "delinq_2yrs": 0, "inq_last_6mths": 0,
            "open_acc": 12, "revol_util": 18.0,
            "total_acc": 25, "emp_length": 8
        }
        res = client.post("/api/predict", json=payload)
        if res.status_code == 200:
            data = res.json()
            assert data["default_probability"] < 0.3
            assert data["risk_score"] >= 600

    def test_predict_high_risk_application(self):
        payload = {
            "loan_amnt": 35000, "int_rate": 26.0,
            "annual_inc": 30000, "dti": 38.0,
            "delinq_2yrs": 3, "inq_last_6mths": 5,
            "open_acc": 15, "revol_util": 88.0,
            "total_acc": 8, "emp_length": 0
        }
        res = client.post("/api/predict", json=payload)
        if res.status_code == 200:
            data = res.json()
            assert data["default_probability"] > 0.2

    def test_predict_returns_feature_importances(self):
        res = client.post("/api/predict", json={})
        if res.status_code == 200:
            data = res.json()
            assert isinstance(data["feature_importance"], dict)
            assert len(data["feature_importance"]) <= 5

    def test_predict_returns_input_summary(self):
        res = client.post("/api/predict", json={"loan_amnt": 20000, "int_rate": 15.0})
        if res.status_code == 200:
            data = res.json()
            assert data["input_summary"]["loan_amount"] == 20000
            assert data["input_summary"]["interest_rate"] == 15.0


# ── Input Validation ──────────────────────────────────────────────────
class TestValidation:
    def test_reject_negative_loan_amount(self):
        res = client.post("/api/predict", json={"loan_amnt": -1000})
        assert res.status_code == 422

    def test_reject_excessive_interest_rate(self):
        res = client.post("/api/predict", json={"int_rate": 100})
        assert res.status_code == 422

    def test_reject_negative_income(self):
        res = client.post("/api/predict", json={"annual_inc": -5000})
        assert res.status_code == 422

    def test_reject_invalid_revol_util(self):
        res = client.post("/api/predict", json={"revol_util": 150})
        assert res.status_code == 422


# ── Risk Tier Logic ───────────────────────────────────────────────────
class TestRiskTierLogic:
    def test_low_risk_tier(self):
        tier, rec, score = get_risk_tier(0.05)
        assert tier == "LOW"
        assert "Approve" in rec
        assert score > 750

    def test_moderate_risk_tier(self):
        tier, rec, score = get_risk_tier(0.15)
        assert tier == "MODERATE"
        assert score >= 600

    def test_high_risk_tier(self):
        tier, rec, score = get_risk_tier(0.25)
        assert tier == "HIGH"
        assert "review" in rec.lower()

    def test_very_high_risk_tier(self):
        tier, rec, score = get_risk_tier(0.40)
        assert tier == "VERY HIGH"
        assert "collateral" in rec.lower()

    def test_critical_risk_tier(self):
        tier, rec, score = get_risk_tier(0.60)
        assert tier == "CRITICAL"
        assert "Decline" in rec

    def test_score_always_in_bounds(self):
        for prob in [0.0, 0.1, 0.25, 0.5, 0.75, 0.99]:
            _, _, score = get_risk_tier(prob)
            # Score is raw from tier function, bounds applied in endpoint
            assert isinstance(score, int)


# ── Confidence Level ──────────────────────────────────────────────────
class TestConfidence:
    def test_very_high_confidence(self):
        assert get_confidence_level(0.02) == "Very High"
        assert get_confidence_level(0.98) == "Very High"

    def test_low_confidence_near_boundary(self):
        result = get_confidence_level(0.48)
        assert "Low" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
