import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text


def build_health_dataset():
    print("Loading CONSTRAINT COVID-19 fake news dataset...")

    train_df = pd.read_csv('Constraint_Train.csv')
    val_df = pd.read_csv('Constraint_Val.csv')
    test_df = pd.read_csv('english_test_with_labels.csv')

    combined = pd.concat([train_df, val_df, test_df], ignore_index=True)
    combined = combined[['tweet', 'label']].rename(columns={'tweet': 'text'})
    combined['label'] = combined['label'].map({'real': 1, 'fake': 0})
    combined = combined.dropna(subset=['text', 'label'])

    # Bonus: fold in the short WHO-style real claims from the CoAID dataset too
    try:
        claim_real = pd.read_csv('ClaimRealCOVID-19.csv')
        extra_real = pd.DataFrame({
            'text': claim_real['title'].fillna(''),
            'label': 1
        })
        extra_real = extra_real[extra_real['text'].str.strip().str.len() > 0]
        combined = pd.concat([combined, extra_real], ignore_index=True)
    except FileNotFoundError:
        pass

    df = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"Health dataset: {len(df)} rows ({(df['label']==1).sum()} real, {(df['label']==0).sum()} fake)")
    return df


def build_finance_dataset():
    print("Loading Bitcoin scam dataset...")
    df = pd.read_csv('Bitcoin_Scam_Detection_Dataset_2025.csv')

    df = df[['message_text', 'label']].rename(columns={'message_text': 'text'})
    df['label'] = df['label'].map({'legit': 1, 'scam': 0})
    df = df.dropna(subset=['text', 'label'])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"Finance dataset: {len(df)} rows ({(df['label']==1).sum()} legit, {(df['label']==0).sum()} scam)")
    return df


def train_and_save(df, model_name):
    df['cleaned'] = df['text'].apply(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )

    pipeline = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), max_features=10000, stop_words='english'),
        LogisticRegression(max_iter=1000, class_weight='balanced')
    )
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    print(f"\n--- {model_name} evaluation ---")
    print(classification_report(y_test, preds, target_names=['Fake/Scam', 'Real/Legit']))

    joblib.dump(pipeline, model_name)
    print(f"Saved {model_name}")


if __name__ == '__main__':
    health_df = build_health_dataset()
    train_and_save(health_df, 'health_model.pkl')

    finance_df = build_finance_dataset()
    train_and_save(finance_df, 'finance_model.pkl')

    print("\nDone! Both models retrained on domain-appropriate data.")