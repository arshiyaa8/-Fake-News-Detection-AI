import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# 1. Clean data utility (mirroring your clean_data.py)
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def train_dual_models():
    print("Loading data...")
    # Loading your True and Fake datasets
    try:
        true_df = pd.read_csv('True.csv')
        fake_df = pd.read_csv('Fake.csv')
    except FileNotFoundError:
        # Fallback if names do not have extensions in your OS view
        true_df = pd.read_csv('True')
        fake_df = pd.read_csv('Fake')

    true_df['label'] = 1
    fake_df['label'] = 0
    
    df = pd.concat([true_df, fake_df]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Use the 'text' or 'title' column depending on your dataset shape
    column_name = 'text' if 'text' in df.columns else df.columns[0]
    
    print("Cleaning text data...")
    df['cleaned'] = df[column_name].apply(clean_text)

    # Keywords to separate finance vs health offline
    finance_keywords = ['crypto', 'finance', 'returns', 'investment', 'bitcoin', 'profit', 'dividend', 'fed', 'sec', 'money', 'stock']
    
    print("Splitting dataset into Health and Finance subjects...")
    # If it contains finance keywords -> finance group. Otherwise -> health group.
    is_finance = df['cleaned'].str.contains('|'.join(finance_keywords), case=False, na=False)
    
    finance_df = df[is_finance]
    health_df = df[~is_finance]

    # Train Health Pipeline
    print(f"Training Health Model ({len(health_df)} samples)...")
    health_pipeline = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), max_features=10000, stop_words='english'),
        MultinomialNB()
    )
    health_pipeline.fit(health_df['cleaned'], health_df['label'])
    joblib.dump(health_pipeline, 'health_model.pkl')

    # Train Finance Pipeline
    print(f"Training Finance Model ({len(finance_df)} samples)...")
    finance_pipeline = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), max_features=10000, stop_words='english'),
        MultinomialNB()
    )
    finance_pipeline.fit(finance_df['cleaned'] if len(finance_df) > 0 else ["dummy scam text"], finance_df['label'] if len(finance_df) > 0 else [0])
    joblib.dump(finance_pipeline, 'finance_model.pkl')

    print("Success! 'health_model.pkl' and 'finance_model.pkl' saved to disk.")

if __name__ == '__main__':
    train_dual_models()