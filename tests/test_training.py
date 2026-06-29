"""
Unit tests for Training Pipeline
==================================
Tests synthetic data generation, model training, and artifact export.
"""

import json
import os
import sys
import tempfile
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.train_model import (
    generate_synthetic_data, train_and_evaluate,
    export_artifacts, FEATURES
)


class TestSyntheticData:
    def test_generates_correct_shape(self):
        df = generate_synthetic_data(n=1000)
        assert len(df) == 1000
        assert all(f in df.columns for f in FEATURES)
        assert "default" in df.columns

    def test_default_rate_is_realistic(self):
        df = generate_synthetic_data(n=10000)
        rate = df["default"].mean()
        assert 0.10 < rate < 0.50, f"Default rate {rate:.2%} is unrealistic"

    def test_feature_ranges_are_valid(self):
        df = generate_synthetic_data(n=5000)
        assert df["loan_amnt"].min() >= 1000
        assert df["loan_amnt"].max() <= 40000
        assert df["int_rate"].min() >= 5.0
        assert df["int_rate"].max() <= 31.0
        assert df["annual_inc"].min() >= 15000
        assert df["revol_util"].min() >= 0
        assert df["revol_util"].max() <= 100
        assert df["emp_length"].min() >= 0
        assert df["emp_length"].max() <= 10

    def test_reproducible_with_seed(self):
        df1 = generate_synthetic_data(n=100, seed=42)
        df2 = generate_synthetic_data(n=100, seed=42)
        assert df1.equals(df2)

    def test_different_seeds_produce_different_data(self):
        df1 = generate_synthetic_data(n=100, seed=42)
        df2 = generate_synthetic_data(n=100, seed=99)
        assert not df1.equals(df2)


class TestTraining:
    @pytest.fixture(scope="class")
    def trained_results(self):
        df = generate_synthetic_data(n=5000, seed=42)
        return train_and_evaluate(df)

    def test_auc_above_minimum(self, trained_results):
        auc = trained_results["metrics"]["auc_roc"]
        assert auc > 0.65, f"AUC-ROC {auc:.3f} is too low — model isn't learning"

    def test_metrics_are_present(self, trained_results):
        m = trained_results["metrics"]
        for key in ["auc_roc", "precision", "recall", "f1_score",
                     "cv_auc_mean", "cv_auc_std", "confusion_matrix"]:
            assert key in m, f"Missing metric: {key}"

    def test_feature_importances_sum_to_one(self, trained_results):
        importances = trained_results["metrics"]["feature_importances"]
        total = sum(importances.values())
        assert abs(total - 1.0) < 0.01, f"Importances sum to {total}"

    def test_confusion_matrix_counts_match(self, trained_results):
        cm = trained_results["metrics"]["confusion_matrix"]
        total = cm["tn"] + cm["fp"] + cm["fn"] + cm["tp"]
        assert total == trained_results["metrics"]["test_size"]


class TestExport:
    def test_artifacts_are_saved(self):
        df = generate_synthetic_data(n=2000, seed=42)
        results = train_and_evaluate(df)

        with tempfile.TemporaryDirectory() as tmpdir:
            export_artifacts(results, tmpdir)

            assert os.path.exists(os.path.join(tmpdir, "credit_model.pkl"))
            assert os.path.exists(os.path.join(tmpdir, "scaler.json"))
            assert os.path.exists(os.path.join(tmpdir, "features.json"))
            assert os.path.exists(os.path.join(tmpdir, "metrics.json"))
            assert os.path.exists(os.path.join(tmpdir, "metadata.json"))

            # Verify JSON files are valid
            with open(os.path.join(tmpdir, "features.json")) as f:
                features = json.load(f)
                assert features == FEATURES

            with open(os.path.join(tmpdir, "scaler.json")) as f:
                scaler = json.load(f)
                assert "mean" in scaler
                assert "scale" in scaler
                assert len(scaler["mean"]) == len(FEATURES)

            with open(os.path.join(tmpdir, "metrics.json")) as f:
                metrics = json.load(f)
                assert "auc_roc" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
