# ArchMail Shield — Email Spam Classifier

ArchMail Shield combines a trained scikit-learn pipeline, a modern Flask API, and a polished web interface to help you flag suspicious emails in seconds. It now ships with a static "browser-only" mode so you can host the UI for free on GitHub Pages while optionally pointing it at a remote inference API.

<br>

## ✨ Highlights

- **ML-powered predictions** — Random Forest pipeline persisted at `models/spam_classifier_pipeline.pkl` and loaded by `src/app.py`.
- **Confidence + calibration** — Probability adjustments driven by curated spam/ham keyword lists to reduce false positives.
- **Two deployment targets**:
  - Dynamic: Flask backend + `templates/index.html` for full model accuracy.
  - Static: `docs/` bundle for GitHub Pages with offline heuristics and optional remote API integration.
- **Transparent diagnostics** — API and static UI expose raw probabilities, adjustments, and keyword hit counts.

<br>

## 📁 Repository layout

```
Task 1 - Email Spam Classifier/
├── data/
│   └── emails.csv
├── docs/                     # Static site ready for GitHub Pages
│   ├── assets/
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
│   └── app.py                # Flask app + model loader + calibration
├── templates/
│   └── index.html            # Flask-rendered UI
├── requirements.txt
└── README.md
```

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

Visit <http://127.0.0.1:8000> to use the full ML-powered interface.

<br>

## 🌐 Static UI on GitHub Pages (free)

1. **Prepare the `docs/` folder** (already present): it contains a static `index.html` with bundled assets.
2. **(Optional) Configure a remote API**
   - Edit `docs/assets/js/config.js` and set `apiBaseUrl` to your hosted Flask endpoint, e.g.:
     ```js
     window.APP_CONFIG = { apiBaseUrl: 'https://archmail-api.onrender.com' };
     ```
   - Alternatively, append query parameters when browsing: `https://<user>.github.io/<repo>/?api=https%3A%2F%2Farchmail-api.onrender.com`.
3. **Commit & push `docs/` to `main`**, then enable GitHub Pages:
   - Repository ➜ Settings ➜ Pages ➜ "Deploy from a branch" ➜ Branch `main`, Folder `/docs`.
4. Wait for the deployment to finish. Your site will be available at `https://<username>.github.io/<repo>/`.

> 🔁 When no API is configured or reachable, the static page falls back to browser-based heuristics using the same keyword calibration logic. This keeps the experience usable on GitHub Pages without backend costs.

<br>

## ⚙️ Configuration options

| Setting | Location | Default | Purpose |
| --- | --- | --- | --- |
| `SPAM_THRESHOLD` | Environment variable (Flask) | `0.7` | Minimum probability required to label an email as spam. |
| `SAFE_KEYWORDS`, `SPAM_KEYWORDS` | `src/app.py` | — | Lists used for probability calibration in the Flask API. |
| `window.APP_CONFIG.apiBaseUrl` | `docs/assets/js/config.js` | `null` | Remote prediction endpoint for the static UI. |
| `window.APP_CONFIG.spamThreshold` | `docs/assets/js/config.js` | `0.7` | Threshold applied in browser mode (also overridable via `?threshold=0.6`). |

<br>

## 🛠️ API reference

- `GET /health` — JSON status indicating whether the model loaded successfully.
- `POST /predict` — Accepts `{ "email_text": "..." }` or form data. Returns:
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

<br>

## ✅ Quick validation snippets

Use Flask’s test client to sanity check predictions without starting the server:

```powershell
python -c "from src.app import app; client = app.test_client();\nprint(client.post('/predict', json={'email_text': 'Win a FREE vacation prize now!'}).get_json())"
```

Test the static heuristic classifier by opening `docs/index.html` directly in a browser or via a local HTTP server:

```powershell
python -m http.server --directory docs 8080
# Navigate to http://127.0.0.1:8080
```

<br>

## 🧱 Tech stack

- Python 3.11, Flask, Flask-CORS
- scikit-learn, pandas, numpy
- Bootstrap 5, vanilla JavaScript

<br>

## 📌 Deployment checklist

- [ ] Push latest changes to `main` (including `docs/`).
- [ ] Enable GitHub Pages (`main` ➜ `/docs`).
- [ ] (Optional) Deploy Flask API to Render/Railway/Fly/Heroku and record the URL.
- [ ] Set `apiBaseUrl` in `docs/assets/js/config.js` or via query string.
- [ ] Smoke test the GitHub Pages site on desktop + mobile.

<br>

Happy filtering! 🛡️✉️
