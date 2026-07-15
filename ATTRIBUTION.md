# Attribution

## Datasets

| Dataset | Used for | Source |
|---|---|---|
| Health misinformation/claims dataset | `health_model.pkl` training | `[FILL IN — link to exact source/Kaggle page used]` |
| Finance misinformation/claims dataset | `finance_model.pkl` training | `[FILL IN — link to exact source used]` |
| Bitcoin Scam Detection Dataset | Part of the finance dataset | `[FILL IN — this is the one open item from the original submission checklist; add the exact source link here before submitting]` |
| General news real/fake dataset (~44,000 articles) | Streamlit demo model training | `[FILL IN — e.g. Kaggle "Fake and Real News Dataset" link, if that's what was used]` |

All datasets were used strictly for training a classifier for this hackathon submission. No copyrighted article text is redistributed as part of this repository — only the resulting trained model files (`.pkl`) and, where applicable, small local sample data (`data/local_news.json`) used for demo purposes.

## Pretrained models

**None.** No pretrained or third-party model weights were downloaded or fine-tuned. Both the health/finance models and the Streamlit demo model were **trained from scratch** on the datasets above using scikit-learn's `TfidfVectorizer` and `LogisticRegression`.

## Libraries and frameworks

### Backend (Flask + models)
| Library | Purpose |
|---|---|
| Flask | Local HTTP server |
| flask-cors | Cross-origin requests from the extension |
| scikit-learn | TF-IDF vectorization + Logistic Regression model |

### Streamlit demo
| Library | Purpose |
|---|---|
| Streamlit | Chat-style UI framework |
| scikit-learn | Model inference |
| duckduckgo_search | Optional online fact-check search |
| SpeechRecognition | Optional voice-to-text input |

### Chrome Extension
| Component | Purpose |
|---|---|
| Chrome Extensions API (Manifest V3) | Context menu, content script injection |

### Website Frontend
| Library | Purpose |
|---|---|
| Next.js | React framework |
| React | UI library |
| Tailwind CSS v4 | Styling |
| shadcn/ui | UI component primitives |
| lucide-react | Icons |
| @react-three/fiber, @react-three/drei, three | 3D visual elements (hero robot scene) |
| @vercel/analytics | Site usage analytics |
| @base-ui/react | UI primitives |
| class-variance-authority, clsx, tailwind-merge | Utility styling helpers |

## License

See `LICENSE` in the project root for the license this project is released under.

## Acknowledgements

Built for **OSDHack 2026** (On-Device AI theme). Core prediction model developed and trained by the project's ML lead (partner); Chrome extension, Flask backend, setup tooling, Streamlit demo integration, and website frontend developed by the rest of the team.
