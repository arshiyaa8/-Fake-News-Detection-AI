import re
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows your browser extension to send data locally

# Load your local offline models
try:
    health_model = joblib.load('health_model.pkl')
    finance_model = joblib.load('finance_model.pkl')
    print("Offline model pipelines successfully loaded.")
except FileNotFoundError:
    print("Warning: Model files missing. Please run train_model.py first.")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def determine_subject(text):
    finance_words = {'crypto', 'finance', 'returns', 'investment', 'bitcoin', 'profit', 'dividend', 'fed', 'sec', 'money', 'wallet', 'scam'}
    words = set(text.split())
    if words.intersection(finance_words):
        return "finance"
    return "health"

@app.route('/diagnose-popup', methods=['POST'])
def diagnose_popup():
    data = request.get_json()
    raw_text = data.get('text', '')
    
    if not raw_text.strip():
        return jsonify({'error': 'Empty string provided'}), 400
        
    cleaned = clean_text(raw_text)
    subject = determine_subject(cleaned)
    
    # Choose correct pipeline
    model = finance_model if subject == "finance" else health_model
    
    # Run prediction locally
    probs = model.predict_proba([cleaned])[0]
    prediction = model.predict([cleaned])[0]
    
    verdict = "REAL" if prediction == 1 else "FAKE"
    confidence = probs[1] if prediction == 1 else probs[0]
    
    return jsonify({
        'subject': subject.upper(),
        'verdict': verdict,
        'confidence': f"{int(confidence * 100)}%"
    })

if __name__ == '__main__':
    app.run(port=5050, debug=False)