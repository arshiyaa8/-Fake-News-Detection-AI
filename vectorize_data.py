import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Load cleaned dataset from Step 2
df = pd.read_csv("cleaned_dataset.csv")

# Drop any rows where clean_text ended up empty/missing
df = df.dropna(subset=["clean_text"])

# Create the TF-IDF vectorizer
# max_features limits vocabulary size to the top 5000 most important words (keeps things fast)
vectorizer = TfidfVectorizer(max_features=5000)

# Fit and transform the cleaned text into numbers
X = vectorizer.fit_transform(df["clean_text"])
y = df["label"]

print("Shape of feature matrix:", X.shape)
print("Shape of labels:", y.shape)

# Save the vectorizer so we can reuse it later (for the Streamlit app etc.)
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

# Save X and y so Step 4 (training) can just load them directly
joblib.dump(X, "X_features.pkl")
joblib.dump(y, "y_labels.pkl")

print("Done! Vectorizer and features saved.")