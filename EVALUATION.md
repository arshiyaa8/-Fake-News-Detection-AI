# Evaluation

## Methodology

Each model (`health_model.pkl`, `finance_model.pkl`, and the Streamlit demo's general-news model) was evaluated using a standard **train/test split** on its respective labeled dataset:

1. Data cleaned and split into train/test sets (a typical 80/20 split; adjust this line to match your actual split if different).
2. TF-IDF vectorizer fit on the training set only, to avoid data leakage from the test set into the vocabulary.
3. Logistic Regression trained on the vectorized training set.
4. Evaluated on the held-out test set using standard classification metrics: accuracy, precision, recall, and F1-score.

> ⚠️ **Fill in your actual metrics.** Report the real numbers from your training script/notebook rather than estimating them:

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| `health_model.pkl` | `[FILL IN]` | `[FILL IN]` | `[FILL IN]` | `[FILL IN]` |
| `finance_model.pkl` | `[FILL IN]` | `[FILL IN]` | `[FILL IN]` | `[FILL IN]` |
| Streamlit demo model (general news) | `[FILL IN]` | `[FILL IN]` | `[FILL IN]` | `[FILL IN]` |

## Baseline comparison

To contextualize the model's performance, compare against a simple baseline — e.g., a majority-class classifier (always predicting the more common label) or a bag-of-words + Naive Bayes model:

| Approach | Accuracy |
|---|---|
| Majority-class baseline | `[FILL IN]` (typically ~50% for a roughly balanced dataset) |
| TF-IDF + Logistic Regression (this project) | `[FILL IN]` |

## Important clarification: confusion matrix scope

If you have a confusion matrix image in your submission materials, **confirm which model it belongs to before including it here.** Based on the project history, an existing confusion matrix image corresponds to the **Streamlit demo's general-news model**, not the health/finance models actually used by the Chrome extension. Label it clearly (or generate separate confusion matrices for `health_model.pkl` and `finance_model.pkl`) so judges don't assume one chart represents all three models.

## Known failure cases / limitations

- **Domain mismatch:** the health and finance models are trained on domain-specific vocabulary. Feeding clearly off-topic text (e.g., sports news) into either model may produce a low-confidence or unreliable verdict, since it's outside the model's training distribution.
- **Sarcasm and satire:** like most TF-IDF-based classifiers, the models key off word patterns rather than deeper semantic understanding, so satirical articles written in a "real news" style can be misclassified.
- **Very short inputs:** a single sentence or headline has far fewer TF-IDF features to work with than a full article, which can reduce confidence or accuracy.
- **Novel/evolving claims:** since the models are trained on a fixed, historical dataset, claims about very recent events (outside the training data's time range) may not match any learned pattern well.
- **No true "unknown" class:** the models always output one of the trained labels — they don't have a built-in "I don't know" option, so genuinely ambiguous input still receives a confident-looking score.

## Suggested future evaluation work

- Cross-validation (k-fold) instead of a single train/test split, for a more robust accuracy estimate.
- A held-out "adversarial" test set of intentionally tricky examples (sarcasm, mixed true/false claims) to stress-test the model beyond its original test split.
- Human evaluation: have a few people manually label a small sample and compare against the model's verdicts to catch systematic blind spots the automated metrics might miss.
