# ArchMail Shield — Email Spam Classifier# Email Spam Classifier

ArchMail Shield is a machine-learning powered spam filter that serves real-time predictions through a Flask API and a responsive Bootstrap front-end. The model was trained on the Enron email corpus and persisted as a scikit-learn pipeline, then enhanced at inference time with lightweight keyword calibration to reduce false positives on day-to-day messages.This project implements a machine learning model to classify emails as spam or legitimate. It includes a complete pipeline from data preprocessing to model deployment with a web interface.

## Features## Project Structure

- 🔍 **Interactive web interface** for pasting any email body and seeing instant results with confidence scores.```

- 🧠 **Persisted Random Forest pipeline** (`models/spam_classifier_pipeline.pkl`) bundled with vocabulary-aware vectorisation.├── data/

- ⚙️ **Configurable spam threshold** via the `SPAM_THRESHOLD` environment variable, plus keyword-based calibration to balance precision/recall.│ └── emails.csv # Email dataset

- 🌐 **REST API endpoint** (`POST /predict`) that accepts JSON or form payloads and returns structured results.├── models/ # Saved model files

- 📊 **Transparent diagnostics** including raw probability, adjustment amount, and keyword hit counts to aid debugging and reporting.├── notebooks/

│ └── email_spam_classification.ipynb # Analysis notebook

## Project structure├── src/

│ └── app.py # Flask application

````├── templates/

Task 1 - Email Spam Classifier/│   └── index.html         # Web interface

├── data/└── README.md

│   └── emails.csv```

├── models/

│   └── spam_classifier_pipeline.pkl## Features

├── notebooks/

│   └── spam_classifier_full.ipynb- Data preprocessing and cleaning

├── src/- Exploratory Data Analysis (EDA)

│   └── app.py- Feature engineering using TF-IDF

├── templates/- Multiple model implementations:

│   └── index.html  - Naive Bayes

└── requirements.txt  - Random Forest

```  - Linear SVM

- Model evaluation and optimization

- `src/app.py` — Flask application, model loader, probability calibration, and API routes.- Web interface for real-time predictions

- `templates/index.html` — Responsive UI that consumes the `/predict` endpoint.

- `models/spam_classifier_pipeline.pkl` — Pickled inference pipeline created in the notebook.## Setup and Installation

- `data/emails.csv` — Source for vocabulary reconstruction when serving predictions.

1. Clone the repository

## Prerequisites2. Create a virtual environment:

````

- Python 3.11 (3.10+ should work, but the project was developed on 3.11.9). python -m venv .venv

- pip for dependency management. ```

- (Optional) PowerShell or another shell for command execution on Windows.3. Activate the virtual environment:

  - Windows: `.venv\Scripts\activate`

## Setup - Unix/Mac: `source .venv/bin/activate`

4. Install requirements:

`powershell   `

# 1. Clone or copy the repository pip install pandas numpy scikit-learn flask nltk jupyter matplotlib seaborn

cd "E:\My CS\InternShips\Machine Learning - ARCH TECHNOLOGIES - SEP 1 to OCT 31 - Year 2025\Task 1 - Email Spam Classifier" ```

# 2. (Recommended) Create and activate a virtual environment## Usage

python -m venv .venv

.\.venv\Scripts\Activate.ps11. Run the Jupyter notebook to train the model:

# 3. Install dependencies ```

pip install -r requirements.txt jupyter notebook notebooks/email_spam_classification.ipynb

`   `

> **Tip:** If you see `ModuleNotFoundError` for Flask or Flask-Cors, ensure the virtual environment is active before installing packages.2. Start the Flask application:

## Running the development server ```

python src/app.py

`powershell   `

# Ensure the virtual environment is active first

$env:FLASK_APP = "src.app"3. Open your browser and navigate to `http://localhost:5000`

python -m flask run --port 8000

````## Model Performance



Open <http://127.0.0.1:8000> in a browser, paste an email body, and submit to receive a spam/ham verdict with confidence and threshold details.The model achieves high accuracy in spam detection through:



## API usage- Comprehensive text preprocessing

- TF-IDF feature extraction

The `/predict` endpoint accepts either JSON or form data. Example JSON request:- Multiple model comparison

- Hyperparameter optimization

```powershell

Invoke-RestMethod \## Web Interface

  -Uri "http://127.0.0.1:8000/predict" \

  -Method Post \The web interface provides:

  -Body (@{ email_text = 'Reminder: Doctor appointment on Monday at 3pm.' } | ConvertTo-Json) \

  -ContentType "application/json"- Simple text input for email content

```- Real-time spam prediction

- Clear visual feedback

Sample JSON response:- Responsive design



```json## Future Improvements

{

  "success": true,- Add support for email file uploads

  "is_spam": false,- Implement additional feature extraction methods

  "probability": 0.69,- Add model retraining capability

  "threshold": 0.7,- Enhance the web interface with more features

  "raw_probability": 0.99,

  "probability_adjustment": -0.30,## License

  "spam_keyword_hits": 0,

  "ham_keyword_hits": 3,MIT License

  "message": "✅ This email looks legitimate."
}
````

## Configuration

- **`SPAM_THRESHOLD`**: Controls the minimum adjusted probability required to label a message as spam. Defaults to `0.7`.

  ```powershell
  $env:SPAM_THRESHOLD = "0.75"
  python -m flask run --port 8000
  ```

- **Keyword calibration**: `src/app.py` contains allow/deny lists (`SAFE_KEYWORDS`, `SPAM_KEYWORDS`) that tweak the raw model probability. Adjust these sets to better reflect your domain.

## Quick validation script

Use the built-in Flask test client for fast checks without starting the server:

```powershell
python -c "from src.app import app; client = app.test_client();\nprint(client.post('/predict', json={'email_text': 'Win a FREE vacation prize now!'}).get_json())"
```

## Model provenance

- Training notebook: `notebooks/spam_classifier_full.ipynb`
- Training data: Enron email corpus variant stored in `data/emails.csv`
- Model artifact: persisted Random Forest pipeline with scaler and vocabulary metadata

Re-training is optional for serving, but if you do re-train, ensure you update `models/spam_classifier_pipeline.pkl` and keep `data/emails.csv` aligned so vectorisation functions correctly.

## Next steps

- Containerise or deploy behind a WSGI server (e.g., gunicorn) for production use.
- For static hosting (e.g., GitHub Pages), consider bundling the inference API separately (serverless function, Flask on Render/Heroku) and point the front-end AJAX calls to that endpoint.
- Add automated tests around `_adjust_probability` to detect regression in calibration heuristics.

Happy filtering! 🛡️✉️
