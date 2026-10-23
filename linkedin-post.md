# LinkedIn Post — Credit Risk API

## Main draft (recommended)

I shipped an end-to-end ML credit risk system, and the most interesting part wasn't the model — it was what broke in production.

The project: a loan default predictor trained on Lending Club data (Gradient Boosting, 0.77 AUC-ROC), served through a FastAPI endpoint on Vercel with a React dashboard on top.

Two problems taught me more than the training did:

1. Pickle doesn't survive serverless. The model loaded fine locally but failed on Vercel's Python runtime. Instead of fighting version pins, I exported the trained trees to a pure-data Python module and reimplemented inference in numpy — no scikit-learn, no pickle at runtime. Verified bit-for-bit against the original model (max probability difference under 2e-11 across 500 random inputs).

2. My probabilities were lying. I upweighted the default class during training to improve recall — which silently inflated every predicted probability. A typical applicant was scoring 47% default risk. The fix: calibrate raw scores back to empirical default rates using the reliability curve from the held-out test set. Same applicant now scores ~27.9%, which matches reality.

A 0.77 AUC model that outputs miscalibrated probabilities is worse than useless in credit decisions — the ranking is right but every number is wrong. Calibration is the difference between a demo and a decision tool.

Live demo: https://credit-risk-api-1eop.vercel.app
Code: https://github.com/Gaze31/credit-risk-api

Stack: scikit-learn → numpy-only inference, FastAPI serverless, React + Tailwind, Vercel.

#MachineLearning #MLEngineering #CreditRisk #FastAPI #Python

---

## Shorter alternative (if you want punchier)

My credit risk model had a 0.77 AUC and was still giving wrong answers.

I upweighted defaults during training to catch more risky loans — good for recall, but it silently inflated every predicted probability. A perfectly average applicant scored 47% default risk. In a real credit pipeline that's not a bug, it's a lawsuit.

Fixed it by calibrating raw scores against the empirical reliability curve from the held-out test set. Now the numbers mean what they say.

Also learned the hard way that pickle doesn't survive serverless — so I exported the model to pure data and rewrote inference in numpy. Verified identical to the original within 2e-11.

Live: https://credit-risk-api-1eop.vercel.app
Code: https://github.com/Gaze31/credit-risk-api

#MachineLearning #MLEngineering #Python

---

## Posting checklist

- Attach 1–2 screenshots. Best options: the risk result view (shows the "calibrated · raw" detail — it proves the calibration story) and the model performance tab. A post with an image gets ~2x the reach of a bare link.
- Post the link in the FIRST COMMENT if reach matters — LinkedIn deprioritizes posts with external links. Or keep it in the post if you care more about clicks than impressions.
- Post Tuesday–Thursday, morning in your timezone.
- Reply to every comment in the first 2 hours. The algorithm rewards early engagement.
- Pin the repo on your GitHub profile before posting — people WILL click through.
