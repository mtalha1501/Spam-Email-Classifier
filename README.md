# ArchMail Shield — Email Spam Classifier

ArchMail Shield combines a trained scikit-learn pipeline, a lightweight Flask API, and a polished static UI so you can flag suspicious emails in seconds. You can run the API locally, deploy it to Render, and serve the front-end for free on GitHub Pages.

<br>

## 🌍 Live deployment

- **Static UI (GitHub Pages):** https://mtalha1501.github.io/Spam-Email-Classifier/
- **Hosted API (Render):** https://spam-email-classifier-app.onrender.com/

The static site automatically targets the hosted API, but you can override the endpoint at runtime using query parameters (see below).

<br>

## ✨ Highlights

- **ML-powered predictions** — Random Forest pipeline persisted at `models/spam_classifier_pipeline.pkl` and loaded by `src/app.py`.
- **Confidence + calibration** — Probability adjustments driven by curated spam/ham keyword lists to reduce false positives.
- **Dual experience**
  - **API mode:** Flask service exposing `/health` and `/predict` endpoints.
  - **Static mode:** `docs/` bundle for GitHub Pages with offline heuristics and optional remote API integration.
- **Transparent diagnostics** — Responses include raw probability, applied adjustment, and keyword hit counts.

<br>

## 📁 Repository layout

```
Task 1 - Email Spam Classifier/
├── data/
│   └── emails.csv
├── docs/                     # Static site ready for GitHub Pages
│   ├── assets/
│   │   ├── favicon.svg
│   │   ├── css/styles.css
│   │   └── js/
│   │       ├── app.js
│   │       └── config.js
│   └── index.html
├── models/
│   └── spam_classifier_pipeline.pkl
├── notebooks/
│   └── spam_classifier_full.ipynb
├── src/
│   └── app.py                # Flask API + model loader + calibration
├── requirements.txt
└── README.md
```

> The Flask app now returns JSON at `/`. Use the static site or a client such as Postman to interact with the API visually.

<br>

## 🚀 Quick start (local Flask API)

```powershell
# 1. Clone or open the repository
cd "E:\My CS\InternShips\Machine Learning - ARCH TECHNOLOGIES - SEP 1 to OCT 31 - Year 2025\Task 1 - Email Spam Classifier"

# 2. (Recommended) create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the API
$env:FLASK_APP = "src.app"
python -m flask run --port 8000
```

Use a REST client to call `http://127.0.0.1:8000/predict`, or open `docs/index.html` locally to exercise the heuristic UI.

<br>

## 🌐 Static UI on GitHub Pages

1. The `docs/` folder already contains the static build. Push changes to `main` to trigger a new Pages deploy.
2. The default configuration targets the Render API. To point elsewhere, edit `docs/assets/js/config.js`:
   ```js
   window.APP_CONFIG = {
     apiBaseUrl: "https://spam-email-classifier-app.onrender.com",
     spamThreshold: 0.7
   };
   ```
3. You can override settings ad-hoc via query parameters:
   - Endpoint: `?api=https%3A%2F%2Fyour-api.example.com`
   - Threshold: `?threshold=0.65`

When no API is reachable, the page falls back to keyword-driven heuristics to keep the demo usable without a backend.

<br>

## 🛠️ API reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | JSON banner describing the API and pointing to `/predict`. |
| `GET` | `/health` | Reports whether the model artifact loaded successfully. |
| `POST` | `/predict` | Accepts `{ "email_text": "..." }` or form data and returns prediction details. |

Sample `/predict` response:

```json
{
  "success": true,
  "is_spam": false,
  "probability": 0.34,
  "threshold": 0.7,
  "raw_probability": 0.84,
  "probability_adjustment": -0.50,
  "spam_keyword_hits": 0,
  "ham_keyword_hits": 5,
  "message": "✅ This email looks legitimate."
}
```

Quick validation snippet (no server startup required):

```powershell
python -c "from src.app import app; client = app.test_client();\nprint(client.post('/predict', json={'email_text': 'Win a FREE vacation prize now!'}).get_json())"
```

<br>

## ⚙️ Configuration options

| Setting | Location | Default | Purpose |
| --- | --- | --- | --- |
| `SPAM_THRESHOLD` | Environment variable (Flask) | `0.7` | Minimum adjusted probability required to label an email as spam. |
| `SAFE_KEYWORDS`, `SPAM_KEYWORDS` | `src/app.py` | — | Keyword lists used for probability calibration in the API. |
| `window.APP_CONFIG.apiBaseUrl` | `docs/assets/js/config.js` | Render URL | Remote prediction endpoint for the static UI. |
| `window.APP_CONFIG.spamThreshold` | `docs/assets/js/config.js` | `0.7` | Threshold applied in browser mode (also overridable via query string). |

<br>

## 📌 Deployment checklist

- [ ] Commit and push latest changes to `main` (including `docs/`).
- [ ] Confirm GitHub Pages is set to `main` ➜ `/docs`.
- [ ] (Optional) Deploy Flask API to Render/Railway/Fly/Heroku and note the URL.
- [ ] Update `docs/assets/js/config.js` or use query parameters to target your API.
- [ ] Smoke test the GitHub Pages site on desktop & mobile.

<br>

## 🧱 Tech stack

- Python 3.11, Flask, Flask-CORS
- scikit-learn, pandas, numpy
- Bootstrap 5, vanilla JavaScript

<br>

Happy filtering! 🛡️✉️
