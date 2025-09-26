from __future__ import annotations

import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from pathlib import Path
from typing import Any, Dict, Tuple
from collections import Counter
import pickle
import re

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "templates"),
)
CORS(app)

MODEL_PATH = BASE_DIR / "models" / "spam_classifier_pipeline.pkl"
SPAM_THRESHOLD = float(os.environ.get("SPAM_THRESHOLD", "0.7"))

SAFE_KEYWORDS = {
    "team", "meeting", "review", "report", "reminder", "doctor", "appointment",
    "thanks", "thank", "appreciate", "invoice", "schedule", "project", "update",
    "attached", "attachment", "quarterly", "minutes", "agenda", "customer",
    "support", "order", "purchase", "ship", "shipping", "delivery", "family",
    "tomorrow", "today", "note", "kind", "regards", "please", "manager"
}

SPAM_KEYWORDS = {
    "free", "win", "winner", "lottery", "prize", "credit", "loan", "urgent",
    "verify", "income", "investment", "bitcoin", "cash", "offer", "discount",
    "click", "limited", "guaranteed", "money", "bonus", "reward", "secret"
}

class SpamClassifierPipeline:
    """Lightweight inference helper persisted from the training notebook."""

    EMAIL_ID_COLUMN = "Email No."
    TARGET_COLUMN = "Prediction"
    _DATA_PATH = BASE_DIR / "data" / "emails.csv"
    _VOCABULARY: list[str] | None = None

    def __init__(self, scaler=None, estimator=None, use_scaler=True):
        self.scaler = scaler
        self.estimator = estimator
        self.use_scaler = use_scaler

    @classmethod
    def _get_vocabulary(cls) -> list[str]:
        if cls._VOCABULARY is None:
            if not cls._DATA_PATH.exists():
                raise FileNotFoundError(f"Vocabulary source not found at {cls._DATA_PATH}")
            df = pd.read_csv(cls._DATA_PATH, nrows=1)
            cls._VOCABULARY = [
                col for col in df.columns
                if col not in {cls.EMAIL_ID_COLUMN, cls.TARGET_COLUMN}
            ]
        return cls._VOCABULARY

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-z0-9']+", text.lower())

    @classmethod
    def _vectorize_texts(cls, texts: list[str]) -> pd.DataFrame:
        vocabulary = cls._get_vocabulary()
        rows = []
        for text in texts:
            tokens = cls._tokenize(text)
            counts = Counter(tokens)
            rows.append([counts.get(term, 0) for term in vocabulary])
        return pd.DataFrame(rows, columns=vocabulary, dtype=float)

    def _transform(self, features: pd.DataFrame):
        if self.use_scaler and self.scaler is not None:
            return self.scaler.transform(features)
        return features.to_numpy()

    def predict(self, texts: list[str]):
        if isinstance(texts, str):
            texts = [texts]
        features = self._vectorize_texts(texts)
        matrix = self._transform(features)
        return self.estimator.predict(matrix)

    def predict_proba(self, texts: list[str]):
        if not hasattr(self.estimator, 'predict_proba'):
            raise AttributeError('Underlying estimator does not provide predict_proba')
        if isinstance(texts, str):
            texts = [texts]
        features = self._vectorize_texts(texts)
        matrix = self._transform(features)
        return self.estimator.predict_proba(matrix)


class _PipelineUnpickler(pickle.Unpickler):
    """Ensures pickled SpamClassifierPipeline resolves to this module at load time."""

    def find_class(self, module: str, name: str):  # pragma: no cover - behaviour delegated
        if name == "SpamClassifierPipeline":
            return SpamClassifierPipeline
        return super().find_class(module, name)


def _load_pipeline(path: Path) -> Any:
    with path.open("rb") as fh:
        return _PipelineUnpickler(fh).load()


def _adjust_probability(probability: float | None, text: str) -> Tuple[float | None, Dict[str, float]]:
    if probability is None:
        return None, {}

    tokens = SpamClassifierPipeline._tokenize(text)
    spam_hits = sum(1 for token in tokens if token in SPAM_KEYWORDS)
    safe_hits = sum(1 for token in tokens if token in SAFE_KEYWORDS)

    spam_boost = min(0.28, spam_hits * 0.07)
    safe_reduction = min(0.5, safe_hits * 0.1)
    adjusted = probability + spam_boost - safe_reduction
    adjusted = max(0.0, min(1.0, adjusted))

    details = {
        "raw_probability": probability,
        "spam_hits": float(spam_hits),
        "safe_hits": float(safe_hits),
        "spam_boost": spam_boost,
        "safe_reduction": safe_reduction,
        "adjustment": spam_boost - safe_reduction,
    }

    return adjusted, details

classifier = None
load_error: str | None = None

try:
    classifier = _load_pipeline(MODEL_PATH)
except FileNotFoundError:
    load_error = f"Model file not found at {MODEL_PATH}"
except Exception as exc:  # pragma: no cover - defensive fallback
    load_error = f"Failed to load model: {exc}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health() -> tuple[Dict[str, Any], int]:
    healthy = load_error is None
    payload: Dict[str, Any] = {
        "status": "ok" if healthy else "error",
        "model_loaded": healthy,
    }
    if not healthy:
        payload["detail"] = load_error
    return payload, (200 if healthy else 503)

@app.route('/predict', methods=['POST'])
def predict():
    if load_error is not None or classifier is None:
        return jsonify({
            'success': False,
            'error': load_error or 'Model failed to initialise.'
        }), 503

    try:
        payload = request.get_json(silent=True) or request.form
        email_text = (payload.get('email_text') or payload.get('text') or '').strip()

        if not email_text:
            return jsonify({
                'success': False,
                'error': 'Email text is required.'
            }), 400

        raw_probability: float | None = None
        probability: float | None = None
        adjustment_details: Dict[str, float] = {}

        if hasattr(classifier, 'predict_proba'):
            proba = classifier.predict_proba([email_text])[0]
            raw_probability = float(proba[1])
            probability, adjustment_details = _adjust_probability(raw_probability, email_text)
        else:
            prediction = classifier.predict([email_text])[0]
            raw_probability = float(bool(prediction))
            probability, adjustment_details = _adjust_probability(raw_probability, email_text)

        final_probability = probability if probability is not None else raw_probability
        if final_probability is None:
            raise RuntimeError('Classifier failed to produce a probability score.')

        is_spam = final_probability >= SPAM_THRESHOLD

        message = '🚨 Spam detected!' if is_spam else '✅ This email looks legitimate.'

        response: Dict[str, Any] = {
            'success': True,
            'is_spam': is_spam,
            'probability': final_probability,
            'threshold': SPAM_THRESHOLD,
            'message': message
        }

        if adjustment_details:
            response.update({
                'raw_probability': adjustment_details.get('raw_probability'),
                'probability_adjustment': adjustment_details.get('adjustment'),
                'spam_keyword_hits': int(adjustment_details.get('spam_hits', 0)),
                'ham_keyword_hits': int(adjustment_details.get('safe_hits', 0)),
            })

        return jsonify(response)
    except Exception as exc:
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)