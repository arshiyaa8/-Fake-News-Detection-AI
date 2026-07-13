"""
Mock Social Feed Demo - shows the Fake News Detector working inside a
Facebook/Twitter-style feed, calling the LOCAL API for each post.

This demonstrates the "any app can use this" idea: this feed is just a
regular app that talks to your on-device API over localhost - the same
way a real social media app could.

Run with:
    streamlit run feed_demo.py
(Make sure the API is also running: uvicorn api:app --reload)
"""

import time
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Feed Demo - Fake News Detector", page_icon="📱", layout="centered")

st.markdown(
    """
    <style>
    .main .block-container { max-width: 620px; padding-top: 1.5rem; }
    .feed-header {
        text-align:center; padding: 1rem; margin-bottom: 1rem;
        border-radius: 12px; background: #111827;
    }
    .post-card {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        background: #1f2937;
    }
    .post-author { font-weight: 600; font-size: 0.95rem; }
    .post-text { margin: 0.5rem 0; line-height: 1.5; }
    .badge-real {
        display:inline-block; padding: 3px 10px; border-radius: 999px;
        background:#064e3b; color:#6ee7b7; font-size:0.78rem; font-weight:600;
    }
    .badge-fake {
        display:inline-block; padding: 3px 10px; border-radius: 999px;
        background:#450a0a; color:#fca5a5; font-size:0.78rem; font-weight:600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feed-header">
        <h2 style="margin:0;">📱 Sample Feed</h2>
        <p style="color:#9ca3af; margin:0.3rem 0 0 0;">
            Every post below is checked automatically by the on-device API
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mock feed posts - mix of real-sounding and fake-sounding
posts = [
    {
        "author": "Aisha K.",
        "text": "The Federal Reserve announced today it will maintain current interest rates, citing stable inflation data from the past quarter.",
    },
    {
        "author": "Rohit S.",
        "text": "BREAKING: Scientists confirm the moon is actually a hologram projected by NASA to hide the truth from the public!!!",
    },
    {
        "author": "Priya M.",
        "text": "Apple reported quarterly earnings that exceeded analyst expectations, with iPhone sales rising 8 percent compared to last year.",
    },
    {
        "author": "Anonymous",
        "text": "Leaked documents reveal secret government program using weather satellites to control public opinion, insider claims before disappearing.",
    },
]


def check_with_api(text: str):
    try:
        response = requests.post(API_URL, json={"text": text}, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "API not running. Start it with: uvicorn api:app --reload"}
    except Exception as e:
        return {"error": str(e)}


for i, post in enumerate(posts):
    st.markdown(
        f"""
        <div class="post-card">
            <div class="post-author">{post['author']}</div>
            <div class="post-text">{post['text']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    placeholder = st.empty()
    with placeholder:
        with st.spinner("Checking..."):
            result = check_with_api(post["text"])

    if "error" in result:
        placeholder.error(f"⚠️ {result['error']}")
    else:
        label = result["label"]
        confidence = result["confidence"]
        badge_class = "badge-real" if label == "REAL" else "badge-fake"
        icon = "✅" if label == "REAL" else "🚩"
        placeholder.markdown(
            f'<span class="{badge_class}">{icon} {label} · {confidence:.0%} confidence</span>',
            unsafe_allow_html=True,
        )

st.divider()
st.caption(
    "This feed is a demo app calling the local Fake News Detector API (api.py) "
    "over localhost - showing how any app could integrate this on-device model."
)
