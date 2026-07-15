"""
Fake News Detection - Local On-Device Chatbot (Streamlit)
--------------------------------------------------------
OSDHack 2026 submission - On Device AI theme.

Core prediction (TF-IDF + Logistic Regression, from Arshiya's training
work) runs 100% locally - no internet needed for that part.

Optional: an "online fact-check" toggle does a best-effort web search
for similar headlines. This part DOES need internet and is clearly
labeled as optional/best-effort - it never runs unless the user turns
it on, and the core on-device prediction always works without it.

Run with:
    streamlit run appbd.py

Note: this is a separate demo from the "Verifi AI" Chrome extension.
This is a chat-style interface for pasting full headlines/articles;
Verifi AI is a right-click-on-any-webpage extension with its own
Flask backend. They are independent tools in this submission.
"""

import html
import re

import streamlit as st

from model_utils import predict, get_word_importance, load_model

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


@st.cache_resource
def get_model():
    return load_model()


get_model()


def render_highlighted_text(original_text: str, flagged_words: set) -> str:
    tokens = original_text.split(" ")
    rendered = []
    for tok in tokens:
        bare = re.sub(r"[^a-zA-Z]", "", tok).lower()
        safe_tok = html.escape(tok)
        if bare in flagged_words:
            rendered.append(
                f'<span style="background-color:#ff4b4b33; border-bottom:2px solid #ff4b4b; '
                f'border-radius:3px; padding:1px 2px;">{safe_tok}</span>'
            )
        else:
            rendered.append(safe_tok)
    return " ".join(rendered)


def build_explanation_sentence(flagged_words: list) -> str:
    words_only = [w for w, contribution in flagged_words if contribution < -0.001]
    if not words_only:
        return (
            "No single word stood out strongly. The decision came from the overall "
            "combination of words rather than one or two specific terms."
        )
    shown = words_only[:5]
    word_list = ", ".join(f"\u201c{w}\u201d" for w in shown)
    return (
        f"flagged largely due to words like {word_list} — terms statistically "
        f"more common in fake articles in the training data."
    )


def confidence_bar_html(confidence: float, label: str) -> str:
    """Render a colored horizontal confidence meter."""
    pct = max(0, min(100, int(confidence * 100)))
    color = "#22c55e" if label == "REAL" else "#ef4444"
    return f"""
    <div style="background:#1f2937; border-radius:8px; height:10px; margin-top:8px; overflow:hidden;">
        <div style="width:{pct}%; background:{color}; height:100%; transition: width 0.4s ease;"></div>
    </div>
    <p style="color:#9ca3af; font-size:0.82rem; margin-top:4px; margin-bottom:0;">Confidence: {confidence:.1%}</p>
    """


def verdict_card_html(label: str, confidence: float, icon: str) -> str:
    """Render the top-level REAL/FAKE verdict as a styled card."""
    is_real = label == "REAL"
    bg = "#052e1a" if is_real else "#3b0a0a"
    border = "#22c55e" if is_real else "#ef4444"
    return f"""
    <div style="border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.6rem;
                background:{bg}; border:1px solid {border};">
        <div style="font-size:1.35rem; font-weight:700; letter-spacing:0.3px;">{icon} {label}</div>
        {confidence_bar_html(confidence, label)}
    </div>
    """


def try_online_fact_check(query: str, max_results: int = 3):
    """
    Best-effort search for similar headlines. Returns a list of
    {title, href} dicts, or None if search failed (no internet, etc).
    This is NOT a guarantee of truth - just surfaces related coverage
    the user can check themselves.
    """
    if not DDGS_AVAILABLE:
        return None
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception:
        return None


# ---------------------------------------------------------------------
# Page setup + styling
# ---------------------------------------------------------------------
st.set_page_config(page_title="Fake News Detector Bot", page_icon="🔍", layout="centered")

st.markdown(
    """
    <style>
    .main .block-container { padding-top: 1.5rem; max-width: 760px; }

    .app-header {
        text-align: center; padding: 1.6rem 1.2rem 1.8rem 1.2rem; margin-bottom: 1rem;
        border-radius: 18px;
        background: radial-gradient(circle at top left, #1e3a5f22, transparent 60%),
                    linear-gradient(135deg, #1f2937 0%, #0f172a 100%);
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }
    .app-header h1 {
        margin-bottom: 0.3rem; font-size: 2rem; font-weight: 800;
        background: linear-gradient(90deg, #6ee7b7, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .app-header p { color: #9ca3af; margin: 0; font-size: 0.95rem; }

    .badge-onDevice {
        display: inline-block; margin-top: 0.7rem; padding: 5px 14px;
        border-radius: 999px; background-color: #064e3b; color: #6ee7b7;
        font-size: 0.78rem; font-weight: 600; transition: transform 0.15s ease;
        border: 1px solid rgba(110,231,183,0.3);
    }
    .badge-onDevice:hover { transform: scale(1.05); }

    .feature-row {
        display: flex; gap: 0.6rem; margin-bottom: 1.2rem;
    }
    .feature-card {
        flex: 1; text-align: center; padding: 0.7rem 0.4rem; border-radius: 12px;
        background: #111827; border: 1px solid rgba(255,255,255,0.06); font-size: 0.78rem;
        color: #cbd5e1; transition: border-color 0.15s ease;
    }
    .feature-card:hover { border-color: rgba(96,165,250,0.4); }
    .feature-card .emoji { font-size: 1.3rem; display:block; margin-bottom: 0.2rem; }

    .highlighted-box {
        padding: 0.8rem 1rem; border-radius: 10px; background-color: #0b0f16;
        border: 1px solid rgba(255,255,255,0.08); line-height: 1.7; font-size: 0.92rem;
        margin-top: 0.5rem;
    }

    .source-link {
        display:block; padding: 6px 0; font-size: 0.88rem; border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .stChatMessage { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-header">
        <h1>🔍 Fake News Detector Bot</h1>
        <p>Chat with it like a messaging app - paste a headline, get a verdict.</p>
        <span class="badge-onDevice">⚡ Core prediction runs 100% on-device</span>
    </div>
    <div class="feature-row">
        <div class="feature-card"><span class="emoji">🧠</span>ML-based<br>verdicts</div>
        <div class="feature-card"><span class="emoji">🔒</span>Runs fully<br>offline</div>
        <div class="feature-card"><span class="emoji">🔍</span>Word-level<br>explanations</div>
        <div class="feature-card"><span class="emoji">🌐</span>Optional<br>fact-check</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.dialog("ℹ️ How it works")
def show_how_it_works():
    st.markdown(
        """
**1. You paste a headline or article.**
The text is cleaned and converted into numeric features using **TF-IDF**
(term frequency–inverse document frequency) — essentially a weighted count
of which words matter most.

**2. A Logistic Regression model scores it.**
This model was trained on roughly **44,000 labeled news articles** (real vs.
fake) and learned which word patterns tend to show up in each. It outputs a
label — `REAL` or `FAKE` — plus a confidence percentage.

**3. Word highlighting (optional).**
If "Explain WHY" is checked, the app looks at which individual words pushed
the prediction most strongly toward "fake" and highlights them in the reply.

**4. Online fact-check (optional, needs internet).**
If enabled, the app does a best-effort web search for similar headlines and
shows related links — this doesn't verify truth, it just gives you sources
to cross-check yourself.

**Everything in steps 1–3 runs 100% on your device.** No text leaves your
computer unless you turn on the online fact-check toggle.
        """
    )
    if st.button("Got it", use_container_width=True):
        st.rerun()


@st.dialog("🧩 Add as browser extension")
def show_extension_guide():
    st.markdown(
        """
Good news — this already exists as a real, working Chrome extension
called **Verifi AI**, separate from this Streamlit chat demo. It runs
its own lightweight Flask backend instead of Streamlit, and lets you
right-click any selected text on **any webpage** to check it, rather
than pasting text into a chat window here.

**To use it:**
1. Open the `Verifi Ai` project folder (not this Streamlit app).
2. Double-click `setup.bat` (Windows) or `setup.sh` (Mac/Linux) — this
   starts the backend and opens Chrome's extensions page for you.
3. In that Chrome tab, turn on **Developer mode**, click
   **Load unpacked**, and select the `extension/` folder.
4. Highlight text on any page, right-click, and choose
   **"Verify Text with Verifi AI."**

This Streamlit chat app and the Verifi AI extension are two separate
tools in this submission — this one is a chat-style interface for
pasting full headlines/articles, while the extension checks text
directly on the page you're already reading.
        """
    )
    if st.button("Got it", use_container_width=True):
        st.rerun()


col1, col2 = st.columns(2)
with col1:
    if st.button("ℹ️ How it works", use_container_width=True):
        show_how_it_works()
with col2:
    if st.button("🧩 Add as extension", use_container_width=True):
        show_extension_guide()

with st.sidebar:
    st.markdown("### 🔍 Fake News Detector")
    st.caption("Settings")
    show_explain = st.checkbox("Explain WHY (highlighted words)", value=True)
    online_check = st.checkbox(
        "🌐 Also try online fact-check (needs internet)",
        value=False,
        help="Best-effort search for similar headlines online. The core prediction above always works offline - this is an optional extra.",
    )
    st.divider()
    st.metric("Training data size", "~44,000 articles")
    st.caption(
        "Core model: TF-IDF + Logistic Regression, trained on ~44,000 labeled news "
        "articles. Runs locally - no text is sent anywhere unless you enable online fact-check."
    )
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------
# Chat state
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! Paste a news headline or article below and I'll check whether it looks REAL or FAKE — entirely on this device.",
        }
    ]

for msg in st.session_state.messages:
    avatar = "🔍" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)

user_input = st.chat_input("Paste a news headline or article...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": html.escape(user_input)})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(html.escape(user_input))

    with st.chat_message("assistant", avatar="🔍"):
        with st.spinner("Analyzing locally..."):
            result = predict(user_input)
            label, confidence = result["label"], result["confidence"]
            icon = "✅" if label == "REAL" else "🚫"

            reply_parts = [verdict_card_html(label, confidence, icon)]

            if show_explain:
                with st.spinner("Figuring out why..."):
                    important_words = get_word_importance(user_input)
                    explanation = build_explanation_sentence(important_words)
                    reply_parts.append(f"\n**Why?** This was {explanation}")

                    flagged = {w.lower() for w, c in important_words if c < -0.001}
                    if flagged:
                        highlighted_html = render_highlighted_text(user_input, flagged)
                        reply_parts.append(f'\n<div class="highlighted-box">{highlighted_html}</div>')

            if online_check:
                with st.spinner("Searching for related coverage online..."):
                    search_results = try_online_fact_check(user_input)

                if search_results is None:
                    reply_parts.append(
                        "\n\n🌐 *Online fact-check unavailable right now (no internet connection, "
                        "or search library not installed). Prediction above is unaffected.*"
                    )
                elif len(search_results) == 0:
                    reply_parts.append(
                        "\n\n🌐 **Online fact-check:** No similar articles found online. "
                        "This doesn't confirm it's fake — it may just be too recent or niche to be indexed."
                    )
                else:
                    links_html = "".join(
                        f'<a class="source-link" href="{r.get("href", "#")}" target="_blank">🔗 {html.escape(r.get("title", "Untitled"))}</a>'
                        for r in search_results
                    )
                    reply_parts.append(
                        f'\n\n🌐 **Online fact-check found related coverage:**\n<div class="highlighted-box">{links_html}</div>\n\n'
                        f"*This shows similar articles exist online - it doesn't independently verify truth, but gives you sources to check yourself.*"
                    )

            full_reply = "\n".join(reply_parts)
            st.markdown(full_reply, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})