"""
Fake News Detector - Local On-Device API
--------------------------------------------------------
OSDHack 2026 - On Device AI theme.

This runs a small local API server. ANY app - a web app, a mobile app,
a browser extension, another Python script - can send it post text and
get back a FAKE/REAL prediction, as long as they're on the same device
or local network. No cloud service is involved at any point.

Run with:
    uvicorn api:app --reload

Then test it, e.g. in your browser at:
    http://127.0.0.1:8000/docs
(FastAPI auto-generates an interactive test page there.)
"""

from fastapi import FastAPI
from pydantic import BaseModel

from model_utils import predict, load_model

app = FastAPI(
    title="Fake News Detector API",
    description="Local, on-device fake news detection. No text ever leaves this machine.",
    version="1.0",
)

# Load the model once when the server starts, not on every request
load_model()


class NewsText(BaseModel):
    text: str


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Fake News Detector API is up. POST text to /predict.",
    }


@app.post("/predict")
def predict_endpoint(item: NewsText):
    """
    Send: {"text": "some headline or article..."}
    Get back: {"label": "FAKE" or "REAL", "confidence": 0.0-1.0}
    """
    result = predict(item.text)
    return result
