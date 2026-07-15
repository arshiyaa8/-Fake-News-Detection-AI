# Architecture

## Overview

Verifi AI has three components that work together but can each run independently:

```
┌─────────────────────────┐      ┌──────────────────────────┐
│   Chrome Extension        │      │   Streamlit Chatbot Demo   │
│   (Manifest V3)            │      │   (companion, chat UI)     │
│                            │      │                            │
│  content.js  ──right─click─┼─►    │  app.py (Streamlit)         │
│  background.js              │      │   └─ model_utils.py         │
└────────────┬───────────────┘      │       (TF-IDF + LogReg)     │
             │ HTTP (localhost)      │                            │
             ▼                       │  Optional: DuckDuckGo       │
┌─────────────────────────┐         │  web search (online,       │
│   Flask Backend            │         │  opt-in only)              │
│   (server/app.py)           │         └──────────────────────────┘
│                            │
│  ├─ health_model.pkl        │      ┌──────────────────────────┐
│  ├─ finance_model.pkl        │      │   Website Frontend          │
│  └─ data/local_news.json     │      │   (Next.js, online-facing)   │
│                            │      │                            │
│  Runs on 127.0.0.1:5050      │      │  Marketing/landing page —   │
│  100% local inference        │      │  hero, features, FAQ,       │
└─────────────────────────┘         │  how-it-works, 3D visual   │
                                     └──────────────────────────┘
```

## Component breakdown

### 1. Chrome Extension + Flask backend (primary submission)

- **`content.js`** injects a right-click context menu option ("Verify Text with Verifi AI") into any webpage and renders the verdict panel once a response comes back.
- **`background.js`** wires up the Manifest V3 context menu and relays the selected text to the local Flask server.
- **`server/app.py`** is a Flask app listening on `127.0.0.1:5050`. It loads `health_model.pkl` and `finance_model.pkl` at startup and exposes an endpoint that takes selected text, runs it through the appropriate model, and returns a label (REAL/FAKE-style verdict) with a confidence score.
- Both models are pre-trained **TF-IDF + Logistic Regression** pipelines (scikit-learn), serialized with `pickle`. No model training happens at runtime — inference only.

### 2. Streamlit Chatbot Demo

- A standalone chat-style interface (`app.py` in its own folder, separate from the Flask backend) built around the same class of model: **TF-IDF + Logistic Regression**, trained on ~44,000 labeled news articles.
- Core prediction (`predict()` in `model_utils.py`) is on-device only.
- Two clearly optional, opt-in features need internet:
  - **Voice input**, transcribed via Google's free Web Speech API.
  - **Online fact-check toggle**, a best-effort DuckDuckGo search for similar headlines — used only to surface related links, never to override the on-device verdict.

### 3. Website Frontend

- A Next.js/React landing page (marketing/informational), not part of the on-device inference pipeline. Explains the project, its on-device approach, and how to try it.

## Model pipeline

```
Raw text
   │
   ▼
Text cleaning / normalization
   │
   ▼
TF-IDF vectorization (term frequency × inverse document frequency)
   │
   ▼
Logistic Regression classifier
   │
   ▼
Label (REAL / FAKE, or health/finance-specific verdict) + confidence score
```

TF-IDF + Logistic Regression was chosen deliberately for the on-device theme: it's lightweight (no GPU, no large weight files), fast at inference time, and interpretable — word-level coefficients can be inspected directly to explain *why* a verdict was reached (used in the "Explain WHY" feature of the Streamlit demo).

## Data flow: local vs. cloud

| Step | Runs where | Needs internet? |
|---|---|---|
| Text selection (extension) or text entry (Streamlit) | Client-side | No |
| TF-IDF vectorization | Local (Flask/Streamlit process) | No |
| Logistic Regression inference | Local (Flask/Streamlit process) | No |
| Verdict + confidence returned to UI | Local | No |
| Word-importance / "Explain WHY" highlighting | Local | No |
| Voice transcription (Streamlit, optional) | Google Web Speech API | **Yes** (opt-in) |
| Online fact-check (Streamlit, optional) | DuckDuckGo search | **Yes** (opt-in) |
| Website frontend | Client browser (static/hosted page) | Yes (it's a website) |

## Design rationale

- **Two separate models (health / finance)** rather than one general classifier, so each is trained and tuned on domain-relevant vocabulary instead of diluting signal across unrelated topics.
- **Flask over a heavier framework** for the local backend: minimal dependencies, fast startup, easy to package for a one-click setup script.
- **No pretrained/downloaded model weights** — models are trained from scratch on the project's own datasets (see `ATTRIBUTION.md`), keeping the entire pipeline self-contained and license-clean.
- **Optional online features are strictly additive**: removing internet access never breaks the core verdict, it only disables the two clearly-labeled extras.
