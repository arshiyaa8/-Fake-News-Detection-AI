# Privacy & Safety

## Data handling

- **Core prediction never leaves the device.** Selected text (extension) or typed/pasted text (Streamlit demo) is sent only to the local Flask server running on `127.0.0.1:5050` (loopback address — not reachable from outside the machine), which returns a verdict and confidence score. No text is transmitted to any external server for the core prediction.
- **No text is logged or persisted** by the core prediction pipeline beyond the lifetime of a single request/response, unless you have explicitly added logging — if so, document exactly what's logged and where here.
- **Two clearly-labeled optional features send data externally**, and only when the user explicitly enables them:
  - **Online fact-check toggle (Streamlit demo):** sends the entered headline/text to DuckDuckGo's search API to find related coverage.
  - **Voice input (Streamlit demo):** sends the recorded audio clip to Google's Web Speech API for transcription.
  Both are off by default and clearly labeled as needing internet in the UI.
- **Website frontend:** as a standard web page, standard web analytics apply (`@vercel/analytics` is included in the frontend dependencies) — this collects typical anonymized usage/traffic analytics, not the text people run through the detector.

## Extension permissions

> ⚠️ Confirm the exact permissions block from your actual `extension/manifest.json` and update this table to match precisely — the entries below are the permissions a context-menu + local-fetch extension like this would typically need:

| Permission | Why it's needed |
|---|---|
| `contextMenus` | To add the "Verify Text with Verifi AI" option to the right-click menu |
| `activeTab` | To read the currently selected text on the active tab when the context menu item is used |
| `storage` (if used) | To persist any user preferences (e.g., last-used mode) locally in the browser |
| Host permission for `http://127.0.0.1:5050/*` | To allow the extension to send the selected text to the local Flask server for inference |

The extension does **not** request broad host permissions (e.g., access to all URLs' content beyond reading the current selection), and does not request permissions related to browsing history, cookies, or other tabs' data.

## Storage

- **Extension:** does not persist selected text or verdicts between sessions unless you've explicitly added local storage for history — document that here if so.
- **Flask backend:** stateless per-request; models are loaded once into memory at startup and are not modified at runtime.
- **Streamlit demo:** chat history is kept in Streamlit's `session_state`, which lives only for the duration of the browser session and is cleared on refresh or via the "Clear chat" button — it is not written to disk.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Text sent to the wrong endpoint (e.g., misconfigured URL pointing externally) | Backend URL is hardcoded to the loopback address `127.0.0.1`, which is not reachable from the network |
| Optional online features silently sending data without user awareness | Both online features (fact-check, voice transcription) are opt-in checkboxes, off by default, with inline UI copy stating they need internet |
| Model misclassification treated as ground truth | UI clearly frames verdicts as a probabilistic classifier output ("confidence: X%"), not a certified fact-check; see `EVALUATION.md` for known limitations |
| Filename collision between the Flask backend and Streamlit demo (both originally named `app.py`) | Each lives in its own dedicated folder (`server/` vs. `streamlit_demo/`) per the repo structure in `README.md` |

## What this project does *not* do

- It does not send any user-entered text to a third-party AI/cloud API for the core verdict.
- It does not collect or transmit personally identifiable information.
- It does not run any code on pages beyond reading the currently selected text when the user explicitly invokes the context menu action.
