"""
app.py
AI Summarization Hub — Main Streamlit Entry Point.

Run with:
    streamlit run app.py
"""

import sys

# Force UTF-8 output on Windows to avoid UnicodeEncodeError with emoji/special chars
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------ #
#  Page config (MUST be first Streamlit call)                          #
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="AI Summarization Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "About": "AI Summarization Hub — Powered by Google Gemini 2.5 Flash",
    },
)

# ------------------------------------------------------------------ #
#  Inject custom CSS                                                   #
# ------------------------------------------------------------------ #
from components.styles import get_css
st.markdown(get_css(), unsafe_allow_html=True)

# ------------------------------------------------------------------ #
#  Page imports                                                        #
# ------------------------------------------------------------------ #
from pages_ import youtube_page, website_page, text_doc_page, settings_page

# ------------------------------------------------------------------ #
#  Sidebar navigation                                                  #
# ------------------------------------------------------------------ #
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <span class="sidebar-logo">🧠</span>
            <div class="sidebar-title">AI Summarization Hub</div>
            <div class="sidebar-subtitle">Powered by Gemini 2.5 Flash</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### 📌 Navigation")
    page = st.radio(
        "Navigate",
        options=[
            "🎥 YouTube Video Summarizer",
            "🌐 Website Summarizer",
            "📄 Text & Document Summarizer",
            "⚙️ Settings & About",
        ],
        label_visibility="collapsed",
        key="nav_radio",
    )

    st.markdown("---")

# ------------------------------------------------------------------ #
#  Route to the selected page                                          #
# ------------------------------------------------------------------ #
if page == "🎥 YouTube Video Summarizer":
    youtube_page.render()

elif page == "🌐 Website Summarizer":
    website_page.render()

elif page == "📄 Text & Document Summarizer":
    text_doc_page.render()

elif page == "⚙️ Settings & About":
    settings_page.render()
