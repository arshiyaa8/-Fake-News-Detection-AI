"""
Fake News Detection - Local On-Device Chatbot (Streamlit)
--------------------------------------------------------

OSDHack 2026 submission - On Device AI theme.

Core prediction (TF-IDF + Logistic Regression, from Arshiya's training
work) runs 100% locally - no internet needed for that part.

Optional: an "online fact-check" toggle does a best-effort web search
restricted to a small set of trusted news/government domains (BBC,
Reuters, AP, WHO, official .gov.in sources). This part DOES need
internet and is clearly labeled as optional/best-effort - it never
runs unless the user turns it on, and the core on-device prediction
always works without it.

Run with:
    streamlit run app.py
"""

import html
import re

import streamlit as st

from model_utils import predict, get_word_importance, load_model

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

TRUSTED_DOMAINS = [
    "bbc.com", "reuters.com", "apnews.com",
    "pib.gov.in", "who.int", ".gov.in"
]


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
                f'<span style="background-color:#ff5e5e33; border-bottom:2px solid #ff5e5e; '
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


def try_online_fact_check(query: str, max_results: int = 3):
    """
    Best-effort search for similar headlines, restricted to a small
    whitelist of trusted news/government domains (see TRUSTED_DOMAINS).
    Returns a list of {title, href} dicts, or None if search failed
    (no internet, etc).

    This is NOT a guarantee of truth - just surfaces related coverage
    from trusted outlets that the user can check themselves.
    """
    if not DDGS_AVAILABLE:
        return None

    try:
        site_filter = " OR ".join(f"site:{d}" for d in TRUSTED_DOMAINS)
        restricted_query = f"{query} ({site_filter})"

        with DDGS() as ddgs:
            results = list(ddgs.text(restricted_query, max_results=max_results))
            return results
    except Exception:
        return None


def filter_trusted(results, trusted_domains=TRUSTED_DOMAINS):
    """Extra safety net: drop any result whose URL isn't from a trusted domain."""
    if not results:
        return []
    return [r for r in results if any(d in r.get("href", "") for d in trusted_domains)]


# ---------------------------------------------------------------------
# Page setup + styling
# ---------------------------------------------------------------------
st.set_page_config(page_title="Fake News Detector Bot", page_icon="🔍", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0a0a0c;
    }
    .main .block-container { padding-top: 1.5rem; max-width: 720px; }

    .app-header {
        text-align: center; padding: 1.1rem 1rem 1.4rem 1rem; margin-bottom: 1rem;
        border-radius: 14px; background-color: #141414;
        border: 1px solid #262626; border-left: 4px solid #6c5ce7;
    }
    .app-header h1 { margin-bottom: 0.2rem; font-size: 1.8rem; color: #f4f4f5; }
    .app-header p { color: #a1a1aa; margin: 0; }
    .badge-onDevice {
        display: inline-block; margin-top: 0.5rem; padding: 4px 12px;
        border-radius: 999px; background-color: #0f2733; color: #00d2ff;
        font-size: 0.78rem; font-weight: 600;
    }

    .highlighted-box {
        padding: 0.8rem 1rem; border-radius: 10px; background-color: #141414;
        border: 1px solid #262626; border-left: 3px solid #ffb703;
        line-height: 1.7; font-size: 0.92rem; margin-top: 0.5rem;
    }
    .source-link {
        display:block; padding: 6px 0; font-size: 0.88rem;
        border-bottom: 1px solid #262626; color: #00d2ff !important;
    }

    .stButton > button {
        background-color: #00d2ff;
        color: #0a0a0c;
        border-radius: 10px;
        border: none;
        font-weight: 700;
    }
    .stButton > button:hover {
        background-color: #6c5ce7;
        color: white;
    }

    [data-testid="stChatMessage"] {
        background-color: #141414;
        border: 1px solid #262626;
        border-radius: 12px;
    }

    section[data-testid="stSidebar"] {
        background-color: #111113;
        border-right: 1px solid #262626;
    }

    ::selection { background-color: #6c5ce744; }
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
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Settings")
    show_explain = st.checkbox("Explain WHY (highlighted words)", value=True)
    online_check = st.checkbox(
        "🌐 Also try online fact-check (needs internet)",
        value=False,
        help="Best-effort search restricted to trusted outlets (BBC, Reuters, AP, WHO, official govt sites). The core prediction above always works offline - this is an optional extra.",
    )
    st.divider()
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
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

user_input = st.chat_input("Paste a news headline or article...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": html.escape(user_input)})
    with st.chat_message("user"):
        st.markdown(html.escape(user_input))

    with st.chat_message("assistant"):
        with st.spinner("Analyzing locally..."):
            result = predict(user_input)
            label, confidence = result["label"], result["confidence"]

        icon = "✅" if label == "REAL" else "🚫"
        reply_parts = [f"### {icon} Predicted: **{label}** \nConfidence: **{confidence:.1%}**"]

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
            with st.spinner("Checking trusted sources online..."):
                search_results = try_online_fact_check(user_input)
                search_results = filter_trusted(search_results)

            if search_results is None:
                reply_parts.append(
                    "\n\n🌐 *Online fact-check unavailable right now (no internet connection, "
                    "or search library not installed). Prediction above is unaffected.*"
                )
            elif len(search_results) == 0:
                reply_parts.append(
                    "\n\n🌐 **Online fact-check:** No matching coverage found from trusted sources "
                    "(BBC, Reuters, AP, WHO, official government sites). "
                    "This means **Cannot Verify** — not necessarily fake. It may just be too recent, "
                    "too niche, or not covered by these specific outlets."
                )
            else:
                links_html = "".join(
                    f'<a class="source-link" href="{r.get("href", "#")}" target="_blank">🔗 {html.escape(r.get("title", "Untitled"))}</a>'
                    for r in search_results
                )
                reply_parts.append(
                    f'\n\n🌐 **Likely Real — verified via trusted source(s):**\n<div class="highlighted-box">{links_html}</div>\n\n'
                    f"*Similar coverage exists from a trusted outlet. This doesn't independently prove "
                    f"every detail is accurate, but it's a strong positive signal.*"
                )

        full_reply = "\n".join(reply_parts)
        st.markdown(full_reply, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_reply})