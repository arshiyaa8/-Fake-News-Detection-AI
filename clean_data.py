import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

# Download stopwords list (only needs to run once)
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = str(text).lower()                     # lowercase
    text = re.sub(r"[^a-z\s]", "", text)          # remove punctuation & numbers
    words = text.split()                          # tokenize (simple split)
    words = [w for w in words if w not in stop_words]  # remove stop words
    return " ".join(words)

# Load the combined dataset from Step 1
df = pd.read_csv("combined_dataset.csv")

print("Cleaning text... this may take a minute for 44,898 rows.")
df["clean_text"] = df["text"].apply(clean_text)

# Save cleaned dataset
df.to_csv("cleaned_dataset.csv", index=False)

print("Done! Here's a preview:")
print(df[["text", "clean_text"]].head())