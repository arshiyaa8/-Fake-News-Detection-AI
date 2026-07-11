import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Load features, labels, and trained model
X = joblib.load("X_features.pkl")
y = joblib.load("y_labels.pkl")
model = joblib.load("fake_news_model.pkl")

# Recreate the same train/test split used in training (same random_state)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Predict on test set
y_pred = model.predict(X_test)

# Build confusion matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Fake", "Real"])

disp.plot(cmap="Blues")
plt.title("Confusion Matrix - Fake News Detection")
plt.savefig("confusion_matrix.png")
plt.show()

print("Confusion matrix saved as confusion_matrix.png")
print(cm)