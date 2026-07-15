# Local AI Verification

This document exists specifically to state, plainly and in one place, what runs on-device versus what needs the internet, and whether any user data ever leaves the device — as required by the OSDHack 2026 submission format.

## What runs fully on-device

| Component | On-device? |
|---|---|
| Text selection / entry (extension or Streamlit) | ✅ Yes |
| TF-IDF vectorization | ✅ Yes |
| Logistic Regression inference (health, finance, and general-news models) | ✅ Yes |
| Verdict + confidence score generation | ✅ Yes |
| Word-importance / "Explain WHY" highlighting | ✅ Yes |

**All of the above run entirely on the local machine, with no network call, no API key, and no cloud dependency of any kind.** The Chrome extension talks only to a Flask server bound to `127.0.0.1` (loopback) — not reachable from outside the device — and the models (`health_model.pkl`, `finance_model.pkl`) are loaded from local disk at startup.

## What requires internet access

| Feature | Requires internet? | Opt-in or always-on? |
|---|---|---|
| Core verdict (extension or Streamlit) | ❌ No | — |
| Voice input transcription (Streamlit demo) | ✅ Yes (Google Web Speech API) | Opt-in — only used if the user records audio via the microphone widget |
| Online fact-check toggle (Streamlit demo) | ✅ Yes (DuckDuckGo search) | Opt-in — off by default, only runs if the user explicitly enables the toggle |
| Website frontend | ✅ Yes (it's a hosted web page) | N/A — this is a marketing/info page, not part of the detection pipeline |

Both internet-dependent features in the actual detection tool are clearly labeled in the UI as needing internet, and both are off unless the user actively turns them on. Disabling internet access entirely does not break or degrade the core verdict in any way — this can be proven live by turning off WiFi and running a prediction.

## Does any user data leave the device?

**Not for the core feature.** Specifically:

- Selected/entered text used for the actual misinformation verdict is **never transmitted outside the local machine**. It goes from the browser/Streamlit UI to the local Flask process and back — both running on the same device, over the loopback network interface.
- If the user explicitly enables the **online fact-check toggle**, the entered text is sent to DuckDuckGo's search API to look up related headlines.
- If the user explicitly enables **voice input**, the recorded audio clip is sent to Google's Web Speech API for transcription.
- No user data is sent to any Anthropic, OpenAI, or other third-party LLM/cloud AI API at any point in this project — the entire classification pipeline is a locally-trained scikit-learn model, not an API-based large language model.

## How to verify this yourself

1. Start the Flask server and load the extension as normal.
2. Turn off WiFi / disconnect from the network entirely.
3. Highlight text on any webpage and run a verification — the verdict panel should appear normally with a label and confidence score.
4. In the Streamlit demo, confirm the core chat prediction still works with WiFi off, and that only the voice input and online fact-check features show a "needs internet" message when attempted offline.
