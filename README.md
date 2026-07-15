# 🛡️ Verifi AI — Offline Fake News Detector

Two tools, one goal: check whether text is reliable or suspicious,
using ML models that run **entirely on your device** — no internet
calls, no data leaving your machine.

1. **Verifi AI (Chrome extension)** — the main submission. Right-click
   any selected text on any webpage to check it instantly.
2. **Fake News Detector Bot (Streamlit demo, `appfed.py`)** — an
   optional chat-style interface where you paste a headline/article
   and get a verdict with word-level explanations.

---

## ✨ Features

- **Two specialized ML models** (extension) — separate TF-IDF +
  Logistic Regression pipelines for Health and Finance/Crypto claims,
  so each learns the vocabulary and patterns specific to its domain
- **Automatic topic routing** — a keyword check decides which model
  handles the selected text
- **Right-click, on any page** — Chrome extension (Manifest V3), works
  on any website via a context-menu item
- **Floating result panel** — draggable, on-page panel showing the
  verdict, confidence %, and topic — no OS notifications to hunt for
- **Offline related-news matching** — cross-references selected text
  against a local, sourced dataset of real health/finance
  misinformation research (WHO, HHS, CIDRAP, Bitcoin Foundation,
  Sumsub) via keyword overlap. Zero network calls.
- **Local Flask backend** — single `/predict` endpoint, runs on
  `127.0.0.1:5050`, nothing leaves your machine
- **Word-level explanations** (Streamlit demo) — highlights which
  specific words pushed a prediction toward "fake"

---

## 🚀 Quickstart — Verifi AI extension (main submission)

**Requirements:** Python 3.8+ and Google Chrome installed.

1. Download / unzip this repo
2. Run the setup script for your OS **from the project root** (the
   folder that directly contains `server/` and `extension/`):

   | OS | How |
   |---|---|
   | Windows | double-click `setup.bat` |
   | Mac / Linux | double-click `setup.sh`, or run `./setup.sh` in a terminal |
   | Any OS | `python3 setup.py` (or `python setup.py`) |

That's it. The script will:
1. Create a virtual environment and install dependencies
2. Start the backend on `http://127.0.0.1:5050`
3. Open `chrome://extensions` **and** a file browser window pointed at
   the `extension/` folder, so you don't have to click through folders
   by hand

Then, in the Chrome tab that opened:
1. Toggle **Developer mode** on (top-right)
2. Click **Load unpacked**
3. Select the `extension/` folder (already open in the file browser —
   drag it in, or just click Select Folder)

Highlight any text on any webpage → right-click → **"Verify Text with
Verifi AI."**

Leave the terminal window open the whole time you're using it — that's
your running backend. Closing it stops the server.

---

## 🤖 Optional: the Streamlit chat demo

A separate, secondary demo — a chat-style interface for pasting full
headlines/articles and getting a verdict with word-level explanations,
plus an optional (internet-required) fact-check search.

```
cd streamlit-demo        # wherever appfed.py lives
pip install -r requirements.txt
streamlit run appfed.py
```

This is independent of the Verifi AI extension — different model
files (`fake_news_model.pkl` + `tfidf_vectorizer.pkl`), different
interface, not required for the main submission to work.

---

## 📁 Repo structure

```
Verifi-AI/
├── setup.py / setup.sh / setup.bat   ← one-click setup for the extension
├── README.md
├── server/
│   ├── app.py                        ← Flask backend, /predict endpoint
│   ├── requirements.txt
│   ├── health_model.pkl              ← trained TF-IDF + LogisticRegression
│   ├── finance_model.pkl             ← trained TF-IDF + LogisticRegression
│   └── data/
│       └── local_news.json           ← offline sourced misinformation dataset
├── extension/
│   ├── manifest.json                 ← Manifest V3 config
│   ├── background.js                 ← context menu + fetch to backend
│   ├── content.js                    ← floating result panel (on-page UI)
│   └── icon.png
└── streamlit-demo/                   ← optional, separate from main submission
    ├── appfed.py
    ├── model_utils.py
    ├── fake_news_model.pkl
    └── tfidf_vectorizer.pkl
```

**Important:** the extension files (`manifest.json`, `background.js`,
`content.js`, `icon.png`) must sit **directly inside** `extension/` —
not nested in a further subfolder. Chrome's "Load unpacked" only looks
one level deep for `manifest.json`.

---

## 🧠 How the extension works

```
Select text on any page
        │
        ▼
Right-click → "Verify Text with Verifi AI"
        │
        ▼
background.js → POST http://127.0.0.1:5050/predict
        │
        ▼
app.py: keyword router decides Health vs Finance
        │
        ▼
TF-IDF + Logistic Regression model → prediction + confidence
        │
        ▼
Local keyword match against data/local_news.json → related sources
        │
        ▼
content.js renders a draggable result panel on the page
```

---

## 🔧 Manual setup (if you'd rather not run the script)

```bash
cd server
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then load `extension/` unpacked as described above.

---

## 🩺 Known limitation (in progress)

The **Health model's accuracy is weaker** than the Finance model's.
Root cause: it was originally trained on a generic 2017
political-news dataset, not real health claims — it had effectively
learned "articles that don't mention money," not health
misinformation patterns. It's since been retrained on the CoAID
COVID-19 dataset, which improved things but is small and imbalanced
(56 fake vs. 1,009 real examples). Retraining on a larger, balanced
dataset (CONSTRAINT COVID-19 Fake News, ~10,700 items, ~52/48 split)
is in progress. The **Finance/crypto-scam model is trained on a
balanced 10,000-message dataset and evaluates around 98.5% accuracy**
on held-out test data.

---

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Server Unreachable" in the panel | Backend isn't running, or crashed on startup | Run `setup.py`/`setup.bat` again from the project root and watch the terminal for errors |
| `ModuleNotFoundError: No module named 'flask'` in the terminal | `requirements.txt` is missing `flask`/`flask-cors` | Add both to `server/requirements.txt`, delete `server/venv`, re-run setup |
| "Manifest file is missing or unreadable" when loading the extension | Selected the wrong folder — `manifest.json` must be directly inside the folder you pick | In "Load unpacked," select `extension/` itself, not its parent folder |
| "Missing required files" when running `setup.py` | Script was run from inside `server/` instead of the project root | `cd ..` back to the folder that contains both `server/` and `extension/`, then re-run |
| No "Verify Text with Verifi AI" menu item on right-click | Extension not loaded yet, or page is a restricted Chrome page | Reload the extension at `chrome://extensions`; test on a normal webpage, not `chrome://` pages or PDFs |
| Right-click menu appears, but nothing happens after clicking it | Extension files were edited but not reloaded | Go to `chrome://extensions`, click the reload icon on the Verifi AI card, then refresh the webpage |
| "Could not establish connection, receiving end does not exist" | Page was open before the extension loaded | Refresh the tab, or re-select the text and try again |
| `local_news.json not found` warning in server logs | File missing or misnamed | Confirm it's exactly `server/data/local_news.json` (lowercase, underscore) |
| `pip install` fails | Python version too old | Install Python 3.8+ from python.org |

---

## 📊 Data sources

`data/local_news.json` contains paraphrased, sourced summaries from
public health/finance misinformation research, including WHO, HHS,
CIDRAP, the Bitcoin Foundation, and Sumsub. No live API calls are
made at runtime — this is a static, offline dataset by design, to
meet the offline/on-device requirement of this project.
