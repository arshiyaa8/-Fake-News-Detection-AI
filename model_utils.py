"""
Shared model loading + prediction logic.
--------------------------------------------------------
This version loads Arshiya's TF-IDF + Logistic Regression model
(fake_news_model.pkl + tfidf_vectorizer.pkl) instead of the PyTorch LSTM.

Used by api.py, app.py, and feed_demo.py so all three always agree.
"""

import re
import joblib
import nltk
from nltk.corpus import stopwords

# Download stopwords list once (safe to call every run - it skips if already present)
nltk.download("stopwords", quiet=True)
STOP_WORDS = set(stopwords.words("english"))

_model = None
_vectorizer = None


def load_model():
    """Loads the model + vectorizer once and caches them in memory."""
    global _model, _vectorizer
    if _model is not None:
        return _model, _vectorizer

    _model = joblib.load("fake_news_model.pkl")
    _vectorizer = joblib.load("tfidf_vectorizer.pkl")
    return _model, _vectorizer


def clean_text(text: str) -> str:
    """
    Must exactly match Arshiya's clean_data.py preprocessing, since the
    vectorizer was fit on text cleaned this exact way.
    """
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    return " ".join(words)


def predict(text: str) -> dict:
    """
    Runs a single prediction. Returns a dict so it's easy to turn into JSON
    for the API, or use directly in a UI.
    label: 1 = REAL, 0 = FAKE  (matches Arshiya's training convention)
    """
    model, vectorizer = load_model()
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])

    proba = model.predict_proba(X)[0]  # [P(fake), P(real)]
    pred_class = model.predict(X)[0]   # 0 or 1

    label = "REAL" if pred_class == 1 else "FAKE"
    confidence = proba[1] if pred_class == 1 else proba[0]
    return {"label": label, "confidence": round(float(confidence), 4)}


def get_word_importance(text: str, top_k: int = 10):
    """
    Explainability for a linear model: each word's contribution to the
    prediction is (its TF-IDF weight in this text) x (its learned
    coefficient). Negative contributions push toward FAKE, positive
    push toward REAL (since class 1 = REAL in Arshiya's training).

    Returns a list of (word, contribution) sorted by how strongly each
    word pushed the prediction toward FAKE (most negative first).
    """
    model, vectorizer = load_model()
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])

    feature_names = vectorizer.get_feature_names_out()
    coefficients = model.coef_[0]  # one coefficient per vocabulary word

    # X is a sparse row vector; nonzero() gives us just the words that appear
    row = X.tocoo()
    contributions = []
    for col, tfidf_value in zip(row.col, row.data):
        word = feature_names[col]
        contribution = tfidf_value * coefficients[col]
        contributions.append((word, contribution))

    # most negative (pushed hardest toward FAKE) first
    contributions.sort(key=lambda x: x[1])
    return contributions[:top_k]
