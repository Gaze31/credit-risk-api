"""
Credit Risk Model Training Pipeline
====================================
Trains a Gradient Boosting classifier on Lending Club loan data,
evaluates performance, and exports to ONNX for lightweight deployment.

Usage:
    python training/train_model.py --data training/data/lending_club.csv
    python training/train_model.py --synthetic  # For development/CI
"""

import argparse
import json
import os
import sys
import warnings
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    roc_auc_score, classification_report, precision_recall_curve,
    confusion_matrix, f1_score, precision_score, recall_score
)
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import calibration_curve

warnings.filterwarnings("ignore", category=FutureWarning)

# ── Feature Configuration ──────────────────────────────────────────────
FEATURES = [
    "loan_amnt", "int_rate", "annual_inc", "dti",
    "delinq_2yrs", "inq_last_6mths", "open_acc",
    "revol_util", "total_acc", "emp_length"
]

TARGET = "loan_status"

# Lending Club target mapping
LC_DEFAULT_STATUSES = [
    "Charged Off", "Default",
    "Late (31-120 days)", "Late (16-30 days)",
    "Does not meet the credit policy. Status:Charged Off"
]
LC_GOOD_STATUSES = [
    "Fully Paid", "Current",
    "Does not meet the credit policy. Status:Fully Paid"
]


def load_lending_club_data(filepath: str) -> pd.DataFrame:
    """Load and preprocess real Lending Club dataset."""
    print(f"Loading Lending Club data from {filepath}...")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  Raw records: {len(df):,}")

    # Filter to known loan statuses
    valid_statuses = LC_DEFAULT_STATUSES + LC_GOOD_STATUSES
    df = df[df[TARGET].isin(valid_statuses)].copy()
    print(f"  After status filter: {len(df):,}")

    # Binary target: 1 = default, 0 = good
    df["default"] = df[TARGET].isin(LC_DEFAULT_STATUSES).astype(int)

    # Clean int_rate (remove % sign if present)
    if df["int_rate"].dtype == object:
        df["int_rate"] = df["int_rate"].str.rstrip("%").astype(float)

    # Clean emp_length
    if "emp_length" in df.columns:
        emp_map = {"< 1 year": 0, "1 year": 1, "10+ years": 10}
        for i in range(2, 10):
            emp_map[f"{i} years"] = i
        df["emp_length"] = df["emp_length"].map(emp_map)

    # Select features + target, drop NaN
    cols_needed = FEATURES + ["default"]
    df = df[cols_needed].dropna()
    print(f"  After cleaning: {len(df):,}")
    print(f"  Default rate: {df['default'].mean():.1%}")

    return df


def generate_synthetic_data(n: int = 32574, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic loan data that mirrors Lending Club distributions.
    Used for development and CI testing only.
    """
    print(f"Generating synthetic data ({n:,} records)...")
    rng = np.random.RandomState(seed)

    df = pd.DataFrame({
        "loan_amnt":      rng.lognormal(mean=9.5, sigma=0.7, size=n).clip(1000, 40000).astype(int),
        "int_rate":       rng.gamma(shape=3.5, scale=3.5, size=n).clip(5.0, 30.99).round(2),
        "annual_inc":     rng.lognormal(mean=11.0, sigma=0.7, size=n).clip(15000, 500000).astype(int),
        "dti":            rng.gamma(shape=4.0, scale=4.5, size=n).clip(0, 50).round(2),
        "delinq_2yrs":    rng.poisson(lam=0.3, size=n).clip(0, 10),
        "inq_last_6mths": rng.poisson(lam=0.8, size=n).clip(0, 8),
        "open_acc":       rng.poisson(lam=11, size=n).clip(1, 50),
        "revol_util":     rng.beta(a=2.5, b=2.5, size=n) * 100,
        "total_acc":      rng.poisson(lam=25, size=n).clip(2, 80),
        "emp_length":     rng.choice(range(0, 11), size=n, p=[
            0.08, 0.07, 0.09, 0.08, 0.07, 0.07, 0.06, 0.06, 0.06, 0.06, 0.30
        ]),
    })
    df["revol_util"] = df["revol_util"].round(2)

    # Realistic default probability based on actual Lending Club patterns
    logit = (
        -1.2
        + 0.12 * (df["int_rate"] - 13)
        + 0.05 * (df["dti"] - 18)
        + 0.35 * df["delinq_2yrs"]
        + 0.20 * df["inq_last_6mths"]
        - 0.000020 * (df["annual_inc"] - 70000)
        + 0.008 * (df["revol_util"] - 50)
        - 0.05 * df["emp_length"]
        + 0.000008 * (df["loan_amnt"] - 15000)
        + rng.normal(0, 0.6, size=n)
    )
    prob = 1 / (1 + np.exp(-logit))
    df["default"] = (rng.random(n) < prob).astype(int)

    print(f"  Default rate: {df['default'].mean():.1%}")
    return df


def train_and_evaluate(df: pd.DataFrame) -> dict:
    """Train model, evaluate with cross-validation, return metrics + artifacts."""
    X = df[FEATURES]
    y = df["default"]

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train):,} | Test: {len(X_test):,}")

    # Scale features
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    # Compute sample weights for class imbalance
    n_good = (y_train == 0).sum()
    n_default = (y_train == 1).sum()
    weight_default = n_good / n_default
    sample_weights = np.where(y_train == 1, weight_default, 1.0)

    # Train Gradient Boosting
    print("Training Gradient Boosting Classifier...")
    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        min_samples_leaf=20,
        random_state=42
    )
    model.fit(X_train_sc, y_train, sample_weight=sample_weights)

    # Cross-validation AUC
    cv_scores = cross_val_score(
        model, X_train_sc, y_train, cv=5, scoring="roc_auc"
    )
    print(f"CV AUC-ROC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Test set evaluation
    y_pred_proba = model.predict_proba(X_test_sc)[:, 1]
    y_pred = model.predict(X_test_sc)

    auc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n{'='*50}")
    print(f"Test AUC-ROC:  {auc:.4f}")
    print(f"Precision:     {precision:.4f}")
    print(f"Recall:        {recall:.4f}")
    print(f"F1 Score:      {f1:.4f}")
    print(f"{'='*50}")
    print(f"\nConfusion Matrix:")
    print(f"  TN={cm[0][0]:,}  FP={cm[0][1]:,}")
    print(f"  FN={cm[1][0]:,}  TP={cm[1][1]:,}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Good', 'Default'])}")

    # Feature importances
    importances = dict(zip(FEATURES, model.feature_importances_.tolist()))
    importances_sorted = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    # Calibration data
    fraction_pos, mean_predicted = calibration_curve(y_test, y_pred_proba, n_bins=10)

    # Precision-Recall curve data
    pr_precision, pr_recall, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)

    metrics = {
        "auc_roc": round(auc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "cv_auc_mean": round(cv_scores.mean(), 4),
        "cv_auc_std": round(cv_scores.std(), 4),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "default_rate": round(y.mean(), 4),
        "confusion_matrix": {
            "tn": int(cm[0][0]), "fp": int(cm[0][1]),
            "fn": int(cm[1][0]), "tp": int(cm[1][1])
        },
        "feature_importances": importances_sorted,
        "calibration": {
            "fraction_positive": fraction_pos.tolist(),
            "mean_predicted": mean_predicted.tolist()
        }
    }

    return {
        "model": model,
        "scaler": scaler,
        "metrics": metrics,
        "X_test": X_test_sc,
        "y_test": y_test.values,
        "y_pred_proba": y_pred_proba
    }


def export_onnx(model, scaler, output_dir: str):
    """Export model to ONNX format for lightweight inference."""
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType

        initial_type = [("float_input", FloatTensorType([None, len(FEATURES)]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type)

        onnx_path = os.path.join(output_dir, "credit_model.onnx")
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"ONNX model saved to {onnx_path}")
        return True
    except ImportError:
        print("WARNING: skl2onnx not installed. Falling back to pickle export.")
        print("  Install with: pip install skl2onnx")
        return False


def export_artifacts(results: dict, output_dir: str):
    """Save all model artifacts for deployment."""
    os.makedirs(output_dir, exist_ok=True)

    model = results["model"]
    scaler = results["scaler"]
    metrics = results["metrics"]

    # Always save pickle as fallback
    with open(os.path.join(output_dir, "credit_model.pkl"), "wb") as f:
        pickle.dump(model, f)

    # Try ONNX export
    onnx_exported = export_onnx(model, scaler, output_dir)

    # Save scaler as JSON (no sklearn needed at inference)
    scaler_params = {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "var": scaler.var_.tolist()
    }
    with open(os.path.join(output_dir, "scaler.json"), "w") as f:
        json.dump(scaler_params, f, indent=2)

    # Also save scaler as pickle (backup)
    with open(os.path.join(output_dir, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    # Save feature list
    with open(os.path.join(output_dir, "features.json"), "w") as f:
        json.dump(FEATURES, f, indent=2)

    # Save metrics
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Save model metadata
    metadata = {
        "model_type": "GradientBoostingClassifier",
        "framework": "scikit-learn",
        "onnx_available": onnx_exported,
        "features": FEATURES,
        "n_features": len(FEATURES),
        "n_estimators": model.n_estimators,
        "max_depth": model.max_depth,
        "learning_rate": model.learning_rate,
        "metrics": {
            "auc_roc": metrics["auc_roc"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1_score"]
        }
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nAll artifacts saved to {output_dir}/")
    print(f"  - credit_model.pkl (sklearn pickle)")
    if onnx_exported:
        print(f"  - credit_model.onnx (ONNX format)")
    print(f"  - scaler.json (StandardScaler params)")
    print(f"  - features.json (feature list)")
    print(f"  - metrics.json (evaluation metrics)")
    print(f"  - metadata.json (model metadata)")


def main():
    parser = argparse.ArgumentParser(description="Train Credit Risk Model")
    parser.add_argument("--data", type=str, help="Path to Lending Club CSV")
    parser.add_argument("--synthetic", action="store_true",
                        help="Use synthetic data (for dev/CI)")
    parser.add_argument("--output", type=str, default="model",
                        help="Output directory for model artifacts")
    args = parser.parse_args()

    if args.data:
        df = load_lending_club_data(args.data)
    elif args.synthetic:
        df = generate_synthetic_data()
    else:
        print("ERROR: Provide --data <path> or --synthetic")
        print("\nTo use Lending Club data:")
        print("  1. Download from: https://www.kaggle.com/datasets/wordsforthewise/lending-club")
        print("  2. Run: python training/train_model.py --data training/data/accepted_2007_to_2018Q4.csv")
        print("\nFor development/CI:")
        print("  Run: python training/train_model.py --synthetic")
        sys.exit(1)

    results = train_and_evaluate(df)
    export_artifacts(results, args.output)

    print(f"\n{'='*50}")
    print("TRAINING COMPLETE")
    print(f"AUC-ROC: {results['metrics']['auc_roc']}")
    print(f"F1:      {results['metrics']['f1_score']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
