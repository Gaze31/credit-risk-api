# Credit Risk Scoring API & Dashboard

> ML-powered loan default prediction. A Gradient Boosting model trained on Lending Club data, served through a FastAPI backend and a React dashboard — deployed as a single app on Vercel.

🔗 **Live demo:** [credit-risk-api-1eop.vercel.app](https://credit-risk-api-1eop.vercel.app) · **📊 Interactive API docs:** `/api/docs`

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![scikit-learn](https://img.shields.io/badge/scikit--learn-GradientBoosting-F7931E?logo=scikitlearn&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What it does

Given ten features from a loan application (amount, interest rate, income, debt-to-income, credit history, etc.), the model returns a **calibrated probability of default**, maps it to a **risk tier** (LOW → CRITICAL), a **300–850 credit score**, a **lending recommendation**, and the **top feature importances** behind the decision. The dashboard lets you score applications interactively, replay history, and inspect model performance.

## Screenshots

<img width="1470" height="956" alt="image" src="https://github.com/user-attachments/assets/708f7473-4d99-447c-9d2a-649166ede769" />
<img width="1470" height="956" alt="image" src="https://github.com/user-attachments/assets/a8ab3d0f-77ff-4729-83d7-6e895d83363a" />
<img width="1470" height="956" alt="image" src="https://github.com/user-attachments/assets/95d54d5d-de87-4171-b3fd-aa7900668a3c" />



---

## Model card

Honesty about a model's limits is a feature, not a weakness. Here is exactly how this model performs.

| Metric | Value | Reading |
|---|---|---|
| **AUC-ROC (test)** | **0.770** | Solid discrimination for consumer credit risk. |
| **AUC-ROC (5-fold CV)** | **0.777 ± 0.004** | Tiny variance → the model is stable and not overfit. |
| **Recall** | **0.703** | Catches ~70% of true defaulters. |
| **Precision** | **0.461** | Of applicants it flags, ~46% actually default. |
| **F1** | **0.557** | Balance of the two. |

**Data:** Lending Club loans. Train 26,059 / Test 6,515. Base default rate **27.3%** (imbalanced — worth stating).

**Confusion matrix (test set):**

|  | Predicted good | Predicted default |
|---|---|---|
| **Actually good** | TN 3,280 | FP 1,459 |
| **Actually default** | FN 527 | TP 1,249 |

**The deliberate tradeoff:** this model is tuned to favor **recall over precision**. In lending, a missed defaulter (false negative) costs the whole loan, while a wrongly-flagged good borrower (false positive) just goes to manual review. Catching 70% of defaulters at the cost of some false alarms is the economically correct bias — and it's a choice, not an accident.

**What drives predictions (feature importance):**

1. Annual income — 40%
2. Interest rate — 31%
3. Debt-to-income ratio — 14%
4. Revolving utilization — 4%
5. (remaining six features share ~11%)

**Limitations (read before trusting it):**

- Trained on historical Lending Club data; it inherits any bias in that data and is **not** validated for real lending decisions.
- Not a regulated credit-scoring system. It performs **no** FCRA/ECOA compliance, adverse-action handling, or fair-lending testing. It is a portfolio/educational demo, not a production underwriting tool.
- Only ten features — real underwriting uses hundreds.

---

## Architecture

```
credit-risk-api/
├── api/index.py          # FastAPI inference service  → /api/*
├── model/                # Pickled GBM + JSON scaler & metrics (~455 KB)
├── training/train_model.py
├── src/                  # React + Vite dashboard (Tailwind, Recharts, lucide)
│   └── components/        # LoanForm, RiskResult, PredictionHistory, ModelMetrics, Header
├── tests/                # pytest: API + training
└── vercel.json           # One deploy: Python serverless + static frontend, same origin
```

**Why one origin:** `vercel.json` builds the Python API and the static React app together, so the frontend calls `/api/*` on its own domain — no CORS gymnastics, no second deployment to babysit.

## API reference

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/api/predict` | Score a loan application → probability, tier, score, recommendation, feature importances. |
| `GET` | `/api/health` | Model status + version. |
| `GET` | `/api/model-info` | Metrics, confusion matrix, feature importances. |
| `GET` | `/api/sample` | Sample low/moderate/high-risk applications for testing. |
| `GET` | `/api/docs` | Interactive Swagger UI. |

Example:

```bash
curl -X POST https://<your-app>.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{"loan_amnt":20000,"int_rate":15,"annual_inc":55000,"dti":22,
       "delinq_2yrs":1,"inq_last_6mths":2,"open_acc":8,"revol_util":55,
       "total_acc":15,"emp_length":3}'
```

## Run locally

```bash
# Backend (terminal 1)
pip install -r requirements.txt
uvicorn api.index:app --reload --port 8000

# Frontend (terminal 2)
npm install
npm run dev          # http://localhost:5173, proxies /api → localhost:8000
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Deploy (Vercel — one project, free tier)

1. Push to GitHub (already done).
2. vercel.com → **Add New → Project** → import this repo.
3. Vercel auto-detects `vercel.json` (Python serverless + static build). Framework preset: **Other**. No env vars needed — frontend and API share one origin.
4. **Deploy.** Your app is live at `https://<project>.vercel.app`, docs at `/api/docs`.

Total footprint is ~1.4 MB and well under Vercel's free-tier limits (100 GB bandwidth/month, 250 MB function size). Unlike Render's free tier, Vercel serverless doesn't cold-sleep, so the demo loads instantly for anyone who opens it.

---

## Tech stack

**ML:** scikit-learn (GradientBoostingClassifier · 200 trees · depth 4 · lr 0.05), NumPy
**Backend:** FastAPI, Pydantic, Uvicorn
**Frontend:** React 18, Vite, Tailwind CSS, Recharts, lucide-react
**Deploy:** Vercel (serverless Python + static)

## License

MIT — built by Sumedha Hundekar. [GitHub](https://github.com/Gaze31/credit-risk-api)
