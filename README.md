# Verifi AI 🔍

**OSDHack 2026 Submission — On-Device AI Theme**

Verifi AI is a misinformation detector with both **offline, on-device** and **online** features. It ships in three parts:

1. **Chrome Extension (Manifest V3)** — the primary submission. Right-click any selected text on any webpage and get an instant **Health** or **Finance** misinformation verdict from a local Flask backend running two offline ML models.
2. **Streamlit Chatbot Demo** — a companion chat-style interface built around a TF-IDF + Logistic Regression fake-news classifier, trained on ~44,000 labeled news articles. Useful for showing the underlying model in a friendlier, conversational format, and includes an optional online fact-check feature.
3. **Website Frontend** — a Next.js/React web app (see [Website Frontend](#website-frontend) below) that serves as the project's online-facing interface.

The core ML verdict always runs **100% locally** with no internet connection required — the website frontend and the optional fact-check toggle are the parts of the project that use the internet.

---

## Why this exists

Misinformation detection tools are usually cloud APIs: your text gets sent to a server you don't control. Verifi AI proves this doesn't have to be the case — the entire classification pipeline (TF-IDF vectorization + Logistic Regression inference) runs on-device, in a local Flask process, with no network calls required to produce a verdict.

---

## What's in this repo

```
Verifi-AI/
├── server/                  # Flask backend + ML models (extension backend)
│   ├── app.py
│   ├── health_model.pkl
│   ├── finance_model.pkl
│   ├── data/local_news.json
│   └── requirements.txt
├── extension/                # Chrome Manifest V3 extension
│   ├── manifest.json
│   ├── background.js
│   └── content.js
├── streamlit_demo/            # Companion chatbot demo (separate app.py)
│   ├── app.py
│   └── model_utils.py
├── website/                   # Next.js web frontend (online-facing UI)
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                  # shadcn/ui primitives
│   │   ├── cta-footer.tsx
│   │   ├── faq.tsx
│   │   ├── features.tsx
│   │   ├── hero.tsx
│   │   ├── how-it-works.tsx
│   │   ├── robot.tsx
│   │   ├── robot-scene.tsx       # React Three Fiber 3D scene
│   │   └── site-header.tsx
│   ├── lib/
│   │   └── utils.ts
│   ├── public/
│   │   ├── apple-icon.png
│   │   ├── icon.ico
│   │   ├── icon-dark-32x32.png
│   │   ├── icon-light-32x32.png
│   │   ├── placeholder.jpg
│   │   ├── placeholder.ico
│   │   ├── placeholder-logo.png
│   │   ├── placeholder-logo.ico
│   │   └── placeholder-user.jpg
│   ├── .gitignore
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   ├── next.config.mjs
│   ├── postcss.config.mjs
│   └── components.json
├── setup.py                  # Cross-platform setup logic
├── setup.sh                  # macOS/Linux wrapper
├── setup.bat                 # Windows wrapper
├── README.md                  # You are here
├── ARCHITECTURE.md
├── TECHNICAL_REPORT.md
├── EVALUATION.md
├── PRIVACY_AND_SAFETY.md
├── ATTRIBUTION.md
```

> ⚠️ **Note:** the Streamlit demo's backend file is also named `app.py`. Keep it in its own `streamlit_demo/` folder, separate from `server/app.py` — if the two ever land in the same directory, one will silently overwrite the other.

---

## Quick Start — Chrome Extension (main submission)

### 1. One-click setup

From the **project root** (the folder containing both `server/` and `extension/`):

**Windows:**
```
setup.bat
```

**macOS/Linux:**
```
./setup.sh
```

This automatically:
- Checks your Python version
- Creates a virtual environment in `server/venv`
- Installs everything in `server/requirements.txt`
- Verifies all required files exist (`app.py`, both `.pkl` models, `data/local_news.json`, extension files) and fails early with a clear message if anything's missing
- Starts the Flask server on `127.0.0.1:5050` and waits until it responds
- Opens `chrome://extensions` and a file browser pointed at the `extension/` folder

### 2. Load the extension in Chrome

1. In the `chrome://extensions` tab that opened automatically, toggle on **Developer mode** (top right).
2. Click **Load unpacked**.
3. Select the `extension` folder (the file browser window that opened points right at it).
4. You should see a **"Verifi AI"** card appear in your extensions list.

### 3. Use it

Highlight any text on any webpage → right-click → **"Verify Text with Verifi AI"** → a panel appears on the page with the verdict and confidence score.

### Manual setup (if `setup.bat`/`setup.sh` doesn't work on your system)

```
cd server
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python app.py
```
Then load the extension manually as in step 2 above.

---

## Quick Start — Streamlit Chatbot Demo

This is a separate, optional companion app: a chat-style interface around the same TF-IDF + Logistic Regression fake-news model.

```
cd streamlit_demo
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`).

**Features:**
- 🧠 Paste a headline or article, get a `REAL`/`FAKE` verdict with a confidence meter — runs entirely on-device
- 🔍 **"Explain WHY"** toggle — highlights the specific words that pushed the prediction, with a plain-English explanation
- 🎤 Optional voice input (needs the `SpeechRecognition` package; needs internet for transcription)
- 🌐 Optional **"online fact-check"** toggle — best-effort web search for similar headlines via DuckDuckGo. This is clearly optional, off by default, and only used to surface related coverage — it never replaces or gates the core on-device prediction

> Core prediction (steps 1–3 of the model pipeline) always runs offline. The only two features that need internet are voice transcription and the optional online fact-check toggle, and both are opt-in.

---

## Quick Start — Website Frontend

A **Next.js 16 / React 19 / TypeScript** web app that provides the project's online-facing interface. It was scaffolded and built using **[v0](https://v0.dev)** (Vercel's AI UI builder), with:

- **Tailwind CSS v4** + **shadcn/ui** (`base-nova` style, `neutral` base color) for the UI
- **Lucide** for icons
- **React Three Fiber** + **drei** + **three.js** for 3D visual elements
- **pnpm** as the package manager (lockfile version 9.0)
- **@vercel/analytics** for usage analytics

### Setup and run

```
cd website
pnpm install
pnpm dev
```

Then open `http://localhost:3000`.

**Other scripts:**
```
pnpm build     # production build
pnpm start     # run the production build
pnpm lint      # lint the codebase
```

### Page structure

The landing page (`app/page.tsx`) is composed of the following sections, in order:

1. `site-header.tsx` — navigation header
2. `hero.tsx` — hero section, paired with `robot-scene.tsx` (an interactive 3D robot built with React Three Fiber + drei)
3. `features.tsx` — feature highlights
4. `how-it-works.tsx` — pipeline walkthrough
5. `faq.tsx` — frequently asked questions
6. `cta-footer.tsx` — call-to-action + footer

Reusable low-level UI primitives (buttons, cards, etc., from shadcn/ui) live in `components/ui/`. Shared helper functions live in `lib/utils.ts`.

### Notes

- `next.config.mjs` sets `typescript.ignoreBuildErrors: true` and `images.unoptimized: true`, so the build won't fail on type errors and images are served unoptimized (useful for quick hackathon deploys, e.g. static export or Vercel).
- Path alias `@/*` is configured in `tsconfig.json`, matching the `@/components`, `@/lib`, `@/hooks`, and `@/components/ui` aliases in `components.json`.
- The `pnpm.overrides` field in `package.json` pins `hono` to `4.12.25` to avoid a dependency conflict.
- `.gitignore` excludes `node_modules`, `.next/`, `.DS_Store`, local env files (`.env*.local`), the Vercel CLI folder (`.vercel/`), and v0 sandbox-only files (`__v0_runtime_loader.js`, `__v0_devtools.tsx`, `__v0_jsx-dev-runtime.ts`, `.snowflake/`, `.v0-trash/`) — none of these should be committed or included in your submission zip.
- Because the app was built in v0's sandbox, double-check before zipping that no leftover `__v0_*` files or `.v0-trash/` folders accidentally got included outside of what `.gitignore` already excludes.

---

## Sample input/output

**Input:** `"Scientists confirm drinking bleach cures COVID-19 overnight"`
**Output:** 🚫 **FAKE** — Confidence: ~94%
**Why:** flagged largely due to words statistically more common in fake articles in the training data (e.g. sensational health claims, absolute language like "cures" and "overnight").

**Input:** `"Federal Reserve raises interest rates by 0.25% following July meeting"`
**Output:** ✅ **REAL** — Confidence: ~88%

---

## Requirements

**Extension + Streamlit demo (offline components):**
- Python 3.9+
- Google Chrome (for the extension)
- See `server/requirements.txt` and `streamlit_demo/requirements.txt` for exact package lists

**Website frontend (online component):**
- Node.js (compatible with Next.js 16 / React 19)
- [pnpm](https://pnpm.io/) package manager
- See `website/package.json` for exact package versions

---

## Further documentation

| Doc | Contents |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System diagram, model pipeline, data flow, local-vs-cloud comparison |
| [TECHNICAL_REPORT.md](./TECHNICAL_REPORT.md) | Model/runtime details, file sizes, quantization rationale, benchmark script and results |
| [EVALUATION.md](./EVALUATION.md) | Accuracy methodology, baseline comparison, known failure cases |
| [PRIVACY_AND_SAFETY.md](./PRIVACY_AND_SAFETY.md) | Data handling, extension permissions, storage, risks |
| [ATTRIBUTION.md](./ATTRIBUTION.md) | Datasets, libraries used, licensing |
| [DEMO_VIDEO_SCRIPT.md](./DEMO_VIDEO_SCRIPT.md) | Shot list for the submission demo video |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Missing dependency | Run setup again — `flask` and `flask-cors` are listed in `requirements.txt` |
| "Manifest file is missing or unreadable" | Wrong folder selected in "Load unpacked" | Make sure `manifest.json` sits directly inside `extension/`, not nested one level deeper |
| "Missing required files" during setup | Setup script run from the wrong directory | Always run `setup.py`/`setup.sh`/`setup.bat` from the project root (the folder containing both `server/` and `extension/`) |
| cmd window closes immediately after double-clicking `setup.bat` | Normal behavior on completion/error | For debugging, open Command Prompt manually, `cd` into the project folder, then run `setup.bat` from there |
| "Server Unreachable" in the extension panel | Flask server isn't running yet | Re-run setup and confirm the terminal shows the server listening on `127.0.0.1:5050` before using the extension |

---

## License

See `LICENSE` in the project root.