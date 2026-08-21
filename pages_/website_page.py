"""
pages_/website_page.py
Website / Webpage Summarizer page.
"""

import streamlit as st
from services.web_service import scrape_url
from services.summarizer import Summarizer
from services.gemini_service import GeminiService
from utils.prompts import WEBSITE_SYSTEM_PROMPT
from utils.analytics import compute_analytics
from components.ui_helpers import (
    render_analytics_metrics,
    render_summary_output,
    render_export_buttons,
    render_settings_sidebar,
    render_strategy_badge,
    render_custom_query_banner,
    render_rich_summary_dynamic,
)


def render():
    st.markdown(
        """
        <div class="page-hero">
            <div class="hero-icon">🌐</div>
            <div>
                <h1 class="hero-title">Website Summarizer</h1>
                <p class="hero-subtitle">
                    Enter any public webpage URL and instantly receive an executive summary,
                    detailed analysis, key insights, and bullet points.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    length, style, strategy, custom_query = render_settings_sidebar(page_key="web")

    # Initialize page session state
    if "web_data" not in st.session_state:
        st.session_state.web_data = None
    if "web_summary_result" not in st.session_state:
        st.session_state.web_summary_result = None
    if "web_active_tab" not in st.session_state:
        st.session_state.web_active_tab = None

    with st.container():
        url = st.text_input(
            "Webpage URL",
            placeholder="https://example.com/article",
            help="Enter a publicly accessible webpage URL.",
            key="web_url_input",
        )
        summarize_btn = st.button(
            "✨ Summarize Website", type="primary", key="web_summarize_btn", use_container_width=False
        )

    if summarize_btn:
        if not url.strip():
            st.warning("⚠️ Please enter a webpage URL.")
            return

        with st.spinner("🌐 Scraping and cleaning webpage content..."):
            try:
                data = scrape_url(url.strip())
                st.session_state.web_data = data
            except ValueError as exc:
                st.error(str(exc))
                st.session_state.web_data = None
                st.session_state.web_summary_result = None
                return

        # Show custom instruction banner
        render_custom_query_banner(custom_query)

        with st.spinner("🤖 Generating AI summary with Gemini..."):
            try:
                gemini = GeminiService()
                summarizer = Summarizer(gemini)
                result = summarizer.summarize(
                    data["text"],
                    WEBSITE_SYSTEM_PROMPT,
                    summary_length=length,
                    summary_style=style,
                    extra_instructions=_build_extra_instructions(custom_query),
                    strategy=strategy,
                )
                st.session_state.web_summary_result = result
                st.session_state.web_active_tab = None
            except (RuntimeError, EnvironmentError) as exc:
                st.error(str(exc))
                st.session_state.web_summary_result = None
                return

    # ---------- Render Results ----------
    if st.session_state.web_data and st.session_state.web_summary_result:
        data = st.session_state.web_data
        result = st.session_state.web_summary_result
        summary = result["summary"]

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("🌐 Page Title", data["title"][:40] + ("..." if len(data["title"]) > 40 else ""))
        mc2.metric("📝 Extracted Words", f"{data['word_count']:,}")
        mc3.metric("🔤 Characters", f"{data['char_count']:,}")

        with st.expander("📄 View Extracted Raw Text", expanded=False):
            st.text_area(
                "Raw Content",
                data["text"][:3000] + ("..." if len(data["text"]) > 3000 else ""),
                height=200,
                disabled=True,
            )

        render_strategy_badge(result["strategy"], result["chunks_used"])
        
        render_rich_summary_dynamic(
            summary=summary,
            page_key="web",
            original_text=data["text"],
            txt_filename="website_summary.txt",
            pdf_title=f"Website Summary: {data['title']}"
        )


def _build_extra_instructions(custom_query: str) -> str:
    if not custom_query or not custom_query.strip():
        return ""
    return (
        f"\n\n⚠️ CRITICAL FORMATTING REQUIREMENT — You MUST follow this exactly:\n"
        f"{custom_query.strip()}\n"
        f"Override any default formatting if needed to honour this instruction."
    )
