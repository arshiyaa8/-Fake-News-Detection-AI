import os
import joblib
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load your models
try:
    print("Loading health model...")
    health_model = joblib.load('health_model.pkl')
    print("Loading finance model...")
    finance_model = joblib.load('finance_model.pkl')
    print("Offline model pipelines successfully loaded.")
except FileNotFoundError as e:
    print(f"Error: Could not find trained model files. Please run 'python train_model.py' first. Details: {e}")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

# Load the local offline news dataset once at startup
try:
    with open('data/local_news.json', 'r', encoding='utf-8') as f:
        LOCAL_NEWS_DB = json.load(f)
    print("Local offline news dataset loaded.")
except FileNotFoundError:
    LOCAL_NEWS_DB = {}
    print("Warning: data/local_news.json not found. Related news will be empty.")

# Fully offline related-news matcher: scores local headlines by keyword overlap
# with the selected text. No internet connection required at any point.
def get_related_news(query_text, subject):
    try:
        cleaned = clean_text(query_text)
        query_words = set(cleaned.split())

        candidates = LOCAL_NEWS_DB.get(subject, [])
        scored = []
        for entry in candidates:
            overlap = len(query_words.intersection(entry.get("keywords", [])))
            if overlap > 0:
                scored.append((overlap, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = [entry for _, entry in scored[:3]]

        if top_matches:
            lines = [f"- {e['headline']} ({e['source']})" for e in top_matches]
            return "\n\n📰 Related (offline dataset, real sourced articles):\n" + "\n".join(lines)

    except Exception as e:
        print(f"Failed to match related news locally: {e}")
    return ""

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'prediction': 'No text provided', 'probability': 0.0, 'subject': 'Unknown'}), 400

        raw_text = data['text']
        cleaned_text = clean_text(raw_text)

        # Keyword router
        finance_keywords = ['crypto', 'finance', 'returns', 'investment', 'bitcoin', 'profit', 'dividend', 'fed', 'sec', 'money', 'stock']
        is_finance = any(word in cleaned_text for word in finance_keywords)

        if is_finance:
            pred_class = finance_model.predict([cleaned_text])[0]
            prob = finance_model.predict_proba([cleaned_text])[0][pred_class]
            subject = "Finance"
        else:
            pred_class = health_model.predict([cleaned_text])[0]
            prob = health_model.predict_proba([cleaned_text])[0][pred_class]
            subject = "Health"

        # If the model is close to a coin flip, be honest about it instead
        # of forcing a confident-sounding label it doesn't actually have.
        if prob < 0.65:
            result_label = "Uncertain"
        else:
            result_label = "Real" if pred_class == 1 else "Suspicious"
        
        # FETCH RELATED NEWS FROM LOCAL OFFLINE DATASET (no internet used)
        related_context = get_related_news(raw_text, subject)

        return jsonify({
            'prediction': result_label,
            'probability': float(prob),
            'subject': subject,
            'related': related_context # Send this back to Chrome
        })

    except Exception as e:
        print(f"Server prediction error: {e}")
        return jsonify({'prediction': 'Error processing text', 'probability': 0.0, 'subject': 'Error', 'related': ''}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=False)