import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
import pickle
import os

np.random.seed(42)
n = 32574

data = pd.DataFrame({
    "loan_amnt":        np.random.randint(1000, 40000, n),
    "int_rate":         np.round(np.random.uniform(5.0, 30.0, n), 2),
    "annual_inc":       np.random.randint(20000, 150000, n),
    "dti":              np.round(np.random.uniform(0, 40, n), 2),
    "delinq_2yrs":      np.random.randint(0, 5, n),
    "inq_last_6mths":   np.random.randint(0, 6, n),
    "open_acc":         np.random.randint(1, 30, n),
    "revol_util":       np.round(np.random.uniform(0, 100, n), 2),
    "total_acc":        np.random.randint(2, 60, n),
    "emp_length":       np.random.randint(0, 11, n),
})

prob_default = (
    0.3 * (data["int_rate"] / 30) +
    0.2 * (data["dti"] / 40) +
    0.15 * (data["delinq_2yrs"] / 5) +
    0.1 * (1 - data["annual_inc"] / 150000) +
    0.1 * (data["revol_util"] / 100) +
    0.15 * np.random.random(n)
)
data["default"] = (prob_default > 0.45).astype(int)

print(f"Dataset: {len(data)} records | Default rate: {data['default'].mean():.1%}")

FEATURES = ["loan_amnt","int_rate","annual_inc","dti",
            "delinq_2yrs","inq_last_6mths","open_acc",
            "revol_util","total_acc","emp_length"]

X = data[FEATURES]
y = data["default"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

model = GradientBoostingClassifier(
    n_estimators=200, max_depth=4,
    learning_rate=0.05, random_state=42)
model.fit(X_train_sc, y_train)

y_pred_proba = model.predict_proba(X_test_sc)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)
print(f"AUC-ROC: {auc:.3f}")
print(classification_report(y_test, model.predict(X_test_sc)))

os.makedirs("model", exist_ok=True)
with open("model/credit_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("model/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("model/features.pkl", "wb") as f:
    pickle.dump(FEATURES, f)

print("Model saved to model/")
