import pandas as pd

# Load both CSV files (they're in this same folder)
true_df = pd.read_csv("True.csv")
fake_df = pd.read_csv("Fake.csv")

# Add label column: 1 = Real, 0 = Fake
true_df["label"] = 1
fake_df["label"] = 0

# Combine title + text into one 'text' column
true_df["text"] = true_df["title"] + " " + true_df["text"]
fake_df["text"] = fake_df["title"] + " " + fake_df["text"]

# Keep only the columns we need
true_df = true_df[["text", "label"]]
fake_df = fake_df[["text", "label"]]

# Combine into one dataset
df = pd.concat([true_df, fake_df], axis=0)

# Shuffle rows
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
df.to_csv("combined_dataset.csv", index=False)

print("Done! Shape of combined dataset:", df.shape)
print(df.head())