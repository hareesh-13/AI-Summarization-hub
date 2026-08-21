"""
pages_/settings_page.py
Settings & configuration page.
"""

import os
import streamlit as st
from dotenv import load_dotenv, set_key
from pathlib import Path


ENV_PATH = Path(__file__).parent.parent / ".env"


def render():
    st.markdown(
        """
        <div class="page-hero">
            <div class="hero-icon">⚙️</div>
            <div>
                <h1 class="hero-title">Settings</h1>
                <p class="hero-subtitle">
                    Configure your API key, model preferences, and application defaults.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------- Summarization parameters --------
    with st.expander("📐 Summarization Parameters", expanded=False):
        st.markdown(
            """
| Parameter | Value |
|-----------|-------|
| Chunk Size | 1,000 characters |
| Chunk Overlap | 200 characters |
| Stuff Strategy Threshold | ≤ 3,000 characters |
| Map-Reduce Threshold | 3,001 – 12,000 characters |
| Refine Strategy | > 12,000 characters |
            """
        )

    # -------- About --------
    with st.expander("ℹ️ About AI Summarization Hub", expanded=False):
        st.markdown(
            """
### AI Summarization Hub
**Version:** 1.0.0  
**Built with:** Python · Streamlit · LangChain · Google Gemini API

**Features:**
- 🎥 YouTube Video Summarizer
- 🌐 Website / Webpage Summarizer
- 📄 Text & Document Summarizer (PDF, DOCX, PPTX, TXT, CSV)
- 📊 Real-time Analytics Dashboard
- 📥 Export as TXT / PDF

**Architecture:**
- Modular service-based design
- Automatic chain strategy selection (Stuff → Map-Reduce → Refine)

---
*Built for production. Optimized for portfolio showcasing.*
            """
        )
