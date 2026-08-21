"""
pages_/text_doc_page.py
Text & Document Summarizer page.
Handles plain text input AND file uploads (PDF, DOCX, PPTX, TXT, CSV).
"""

import streamlit as st
from services.document_service import extract_text
from services.summarizer import Summarizer
from services.gemini_service import GeminiService
from utils.prompts import TEXT_SYSTEM_PROMPT, DOCUMENT_SYSTEM_PROMPT
from utils.analytics import compute_analytics
from components.ui_helpers import (
    render_settings_sidebar,
    render_strategy_badge,
    render_custom_query_banner,
    render_rich_summary_dynamic,
)

SUPPORTED_FORMATS = ["pdf", "docx", "pptx", "txt", "csv"]


def render():
    st.markdown(
        """
        <div class="page-hero">
            <div class="hero-icon">📄</div>
            <div>
                <h1 class="hero-title">Text & Document Summarizer</h1>
                <p class="hero-subtitle">
                    Paste any text or upload PDF, DOCX, PPTX, TXT, or CSV files
                    to generate professional AI-powered summaries.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    length, style, strategy, custom_query = render_settings_sidebar(page_key="doc")

    # Initialize page session state
    if "txt_data" not in st.session_state:
        st.session_state.txt_data = None
    if "txt_summary_result" not in st.session_state:
        st.session_state.txt_summary_result = None
    if "txt_active_tab" not in st.session_state:
        st.session_state.txt_active_tab = None

    if "doc_data" not in st.session_state:
        st.session_state.doc_data = None
    if "doc_summary_result" not in st.session_state:
        st.session_state.doc_summary_result = None
    if "doc_active_tab" not in st.session_state:
        st.session_state.doc_active_tab = None

    # ---------- Input tabs ----------
    tab_text, tab_doc = st.tabs(["✍️ Paste Text", "📁 Upload Document"])

    # ======================== TAB 1: Text input ========================
    with tab_text:
        text_input = st.text_area(
            "Paste your text here",
            placeholder=(
                "Paste an email, article, blog post, report, "
                "social media post, or any other text..."
            ),
            height=300,
            key="text_input_area",
        )
        col1, col2 = st.columns([1, 3])
        with col1:
            text_btn = st.button(
                "✨ Summarize Text", type="primary", key="text_summarize_btn", use_container_width=True
            )

        if text_btn:
            if not text_input.strip():
                st.warning("⚠️ Please paste some text first.")
            elif len(text_input.strip()) < 50:
                st.warning("⚠️ Text is too short to summarize. Please provide at least 50 characters.")
            else:
                data = {
                    "text": text_input.strip(),
                    "word_count": len(text_input.strip().split()),
                    "char_count": len(text_input.strip())
                }
                _run_summarization(
                    text=text_input.strip(),
                    system_prompt=TEXT_SYSTEM_PROMPT,
                    length=length,
                    style=style,
                    custom_query=custom_query,
                    strategy=strategy,
                    session_data_key="txt_data",
                    session_result_key="txt_summary_result",
                    session_tab_key="txt_active_tab",
                    data=data
                )
                
        # Render Text Results
        if st.session_state.txt_data and st.session_state.txt_summary_result:
            data = st.session_state.txt_data
            result = st.session_state.txt_summary_result
            summary = result["summary"]
            
            render_custom_query_banner(custom_query)
            
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("📄 Source", "Pasted Text")
            mc2.metric("📝 Words", f"{data['word_count']:,}")
            mc3.metric("🔤 Characters", f"{data['char_count']:,}")
            
            with st.expander("📄 View Original Text", expanded=False):
                st.text_area("Original Content", data["text"][:3000] + ("..." if len(data["text"]) > 3000 else ""), height=200, disabled=True)

            render_strategy_badge(result["strategy"], result["chunks_used"])
            
            render_rich_summary_dynamic(
                summary=summary,
                page_key="txt_tab",
                original_text=data["text"],
                txt_filename="text_summary.txt",
                pdf_title="Text Summary"
            )

    # ======================== TAB 2: Document upload ========================
    with tab_doc:
        st.markdown("**Supported Formats:** PDF · DOCX · PPTX · TXT · CSV")
        uploaded_file = st.file_uploader(
            "Upload your document",
            type=SUPPORTED_FORMATS,
            key="doc_uploader",
        )

        if uploaded_file:
            st.success(f"✅ Uploaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

        doc_btn = st.button(
            "✨ Summarize Document", type="primary", key="doc_summarize_btn"
        )

        if doc_btn:
            if not uploaded_file:
                st.warning("⚠️ Please upload a document first.")
            else:
                with st.spinner(f"📂 Extracting text from {uploaded_file.name}..."):
                    try:
                        data = extract_text(uploaded_file)
                    except ValueError as exc:
                        st.error(str(exc))
                        return

                _run_summarization(
                    text=data["text"],
                    system_prompt=DOCUMENT_SYSTEM_PROMPT,
                    length=length,
                    style=style,
                    custom_query=custom_query,
                    strategy=strategy,
                    session_data_key="doc_data",
                    session_result_key="doc_summary_result",
                    session_tab_key="doc_active_tab",
                    data=data
                )
                
        # Render Document Results
        if st.session_state.doc_data and st.session_state.doc_summary_result:
            data = st.session_state.doc_data
            result = st.session_state.doc_summary_result
            summary = result["summary"]
            
            render_custom_query_banner(custom_query)

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("📄 File Type", data["file_type"])
            mc2.metric("📝 Words Extracted", f"{data['word_count']:,}")
            mc3.metric("🔤 Characters", f"{data['char_count']:,}")

            with st.expander("📄 Preview Extracted Text", expanded=False):
                preview = data["text"][:2000] + ("..." if len(data["text"]) > 2000 else "")
                st.text_area("Extracted Content", preview, height=200, disabled=True)

            render_strategy_badge(result["strategy"], result["chunks_used"])
            
            render_rich_summary_dynamic(
                summary=summary,
                page_key="doc_tab",
                original_text=data["text"],
                txt_filename=f"{data['filename']}_summary.txt",
                pdf_title=f"Document Summary: {data['filename']}"
            )


def _build_extra_instructions(custom_query: str) -> str:
    if not custom_query or not custom_query.strip():
        return ""
    return (
        f"\n\n⚠️ CRITICAL FORMATTING REQUIREMENT — You MUST follow this exactly:\n"
        f"{custom_query.strip()}\n"
        f"Override any default formatting if needed to honour this instruction."
    )


def _run_summarization(
    text, system_prompt, length, style, custom_query, strategy,
    session_data_key, session_result_key, session_tab_key, data
):
    with st.spinner("🤖 Generating AI summary with Gemini..."):
        try:
            gemini = GeminiService()
            summarizer = Summarizer(gemini)
            result = summarizer.summarize(
                text,
                system_prompt,
                summary_length=length,
                summary_style=style,
                extra_instructions=_build_extra_instructions(custom_query),
                strategy=strategy,
            )
            st.session_state[session_result_key] = result
            st.session_state[session_data_key] = data
            st.session_state[session_tab_key] = None
        except (RuntimeError, EnvironmentError) as exc:
            st.error(str(exc))
            st.session_state[session_result_key] = None
            return
