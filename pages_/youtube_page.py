"""
pages_/youtube_page.py
YouTube Video Summarizer page.
"""

import streamlit as st
from services.youtube_service import get_transcript
from services.summarizer import Summarizer
from services.gemini_service import GeminiService
from utils.prompts import YOUTUBE_SYSTEM_PROMPT
from utils.analytics import compute_analytics
from services.export_service import export_txt, export_pdf
from components.ui_helpers import (
    render_analytics_metrics,
    render_summary_output,
    render_export_buttons,
    render_settings_sidebar,
    render_strategy_badge,
    render_custom_query_banner,
)


def parse_sections(summary_text: str) -> dict:
    """Parse the markdown summary into separate sections based on headings."""
    sections = {
        "quick": "",
        "detailed": "",
        "takeaways": "",
        "topics": ""
    }
    
    current_key = "quick"
    current_lines = []
    
    for line in summary_text.splitlines():
        lower_line = line.strip().lower()
        if line.startswith("## "):
            # Save previous section
            if current_lines:
                sections[current_key] = "\n".join(current_lines).strip()
                current_lines = []
            
            # Identify new section
            if "quick" in lower_line:
                current_key = "quick"
            elif "detailed" in lower_line:
                current_key = "detailed"
            elif "takeaways" in lower_line:
                current_key = "takeaways"
            elif "action" in lower_line:
                # Include action items under takeaways
                current_key = "takeaways"
                current_lines.append(line)
            elif "topic" in lower_line or "subject" in lower_line:
                current_key = "topics"
            else:
                current_key = "detailed"
                current_lines.append(line)
        else:
            current_lines.append(line)
            
    if current_lines:
        sections[current_key] = "\n".join(current_lines).strip()
        
    return sections


def format_topics(topics_text: str) -> str:
    """Format topics to display one per line as bullet points, splitting inline items."""
    # Normalize inline bullet characters to newlines
    normalized = topics_text.replace("•", "\n").replace("-", "\n").replace("*", "\n")
    
    items = []
    # If it was comma-separated and not split by newlines
    if "," in normalized and "\n" not in normalized:
        items = normalized.split(",")
    else:
        for line in normalized.splitlines():
            clean_line = line.strip()
            if not clean_line:
                continue
            # Strip numbered list prefix (e.g. 1.)
            if clean_line and clean_line[0].isdigit():
                parts = clean_line.split(".", 1)
                if len(parts) > 1 and parts[0].isdigit():
                    clean_line = parts[1].strip()
            if clean_line:
                items.append(clean_line)
                
    return "\n\n".join(f"• {item.strip()}" for item in items if item.strip())


def format_takeaways(takeaways_text: str) -> str:
    """Format takeaways and action items with clear spacing and bullet points."""
    lines = []
    for line in takeaways_text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        
        # Convert H2 headers to H3 headers (e.g., ## Action Items -> ### Action Items)
        if clean.startswith("## "):
            lines.append(f"### {clean[3:].strip()}")
            continue
        if clean.startswith("### "):
            lines.append(clean)
            continue
            
        # Standardize existing bullets
        is_bullet = False
        for prefix in ["- ", "* ", "• "]:
            if clean.startswith(prefix):
                lines.append(f"• {clean[len(prefix):].strip()}")
                is_bullet = True
                break
        if is_bullet:
            continue
            
        # Treat raw text lines as bullet points
        lines.append(f"• {clean}")
        
    return "\n\n".join(lines)


def render():
    st.markdown(
        """
        <div class="page-hero">
            <div class="hero-icon">🎥</div>
            <div>
                <h1 class="hero-title">YouTube Video Summarizer</h1>
                <p class="hero-subtitle">
                    Paste any YouTube URL and get AI-powered summaries, key takeaways,
                    action items and topic breakdowns — instantly.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize page session state
    if "yt_video_data" not in st.session_state:
        st.session_state.yt_video_data = None
    if "yt_summary_result" not in st.session_state:
        st.session_state.yt_summary_result = None
    if "yt_active_tab" not in st.session_state:
        st.session_state.yt_active_tab = None

    # ---------- Sidebar settings ----------
    length, style, strategy, custom_query = render_settings_sidebar(page_key="yt")

    # ---------- Input ----------
    url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste any YouTube video URL with captions available.",
        key="yt_url_input",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        summarize_btn = st.button(
            "✨ Summarize", type="primary", key="yt_summarize_btn", use_container_width=True
        )

    # ---------- Logic ----------
    if summarize_btn:
        if not url.strip():
            st.warning("⚠️ Please enter a YouTube URL.")
            return

        with st.spinner("🔍 Fetching transcript from YouTube..."):
            try:
                data = get_transcript(url.strip())
                st.session_state.yt_video_data = data
            except ValueError as exc:
                st.error(str(exc))
                st.session_state.yt_video_data = None
                st.session_state.yt_summary_result = None
                return

        # Show custom instruction banner
        render_custom_query_banner(custom_query)

        with st.spinner("🤖 Generating AI summary with Gemini..."):
            try:
                gemini = GeminiService()
                summarizer = Summarizer(gemini)
                result = summarizer.summarize(
                    data["transcript"],
                    YOUTUBE_SYSTEM_PROMPT,
                    summary_length=length,
                    summary_style=style,
                    extra_instructions=_build_extra_instructions(custom_query),
                    strategy=strategy,
                )
                st.session_state.yt_summary_result = result
                st.session_state.yt_active_tab = None  # Reset active sub-section
            except (RuntimeError, EnvironmentError) as exc:
                st.error(str(exc))
                st.session_state.yt_summary_result = None
                return

    # ---------- Render Results ----------
    if st.session_state.yt_video_data and st.session_state.yt_summary_result:
        data = st.session_state.yt_video_data
        result = st.session_state.yt_summary_result
        summary = result["summary"]
        
        # Show video metadata without card wrapper
        st.markdown("### 🎬 Video Details")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Title", data["title"][:40] + ("..." if len(data["title"]) > 40 else ""))
        mc2.metric("Transcript Words", f"{data['word_count']:,}")
        mc3.metric("Characters", f"{data['char_count']:,}")

        # Parse sections
        sections = parse_sections(summary)

        # Show strategy badge
        render_strategy_badge(result["strategy"], result["chunks_used"])

        # Display Quick Summary (Always visible)
        st.markdown("### 🎯 Quick Summary")
        st.markdown(f'<div class="summary-card">{sections["quick"]}</div>', unsafe_allow_html=True)

        # Dynamic Selection Options
        st.markdown("### 🔍 Explore Further")
        
        det_type = "primary" if st.session_state.yt_active_tab == "detailed" else "secondary"
        take_type = "primary" if st.session_state.yt_active_tab == "takeaways" else "secondary"
        top_type = "primary" if st.session_state.yt_active_tab == "topics" else "secondary"

        col_det, col_take, col_top = st.columns(3)
        with col_det:
            if st.button("📋 Detailed Summary", type=det_type, use_container_width=True, key="opt_detailed"):
                st.session_state.yt_active_tab = "detailed"
                st.rerun()
        with col_take:
            if st.button("🔑 Key Takeaways", type=take_type, use_container_width=True, key="opt_takeaways"):
                st.session_state.yt_active_tab = "takeaways"
                st.rerun()
        with col_top:
            if st.button("📌 Important Topics Covered", type=top_type, use_container_width=True, key="opt_topics"):
                st.session_state.yt_active_tab = "topics"
                st.rerun()

        # Determine active content for rendering and analytics
        active_content = sections["quick"]
        active_heading = "Quick Summary"

        if st.session_state.yt_active_tab == "detailed" and sections["detailed"]:
            active_content = sections["detailed"]
            active_heading = "Detailed Summary"
        elif st.session_state.yt_active_tab == "takeaways" and sections["takeaways"]:
            active_content = format_takeaways(sections["takeaways"])
            active_heading = "Key Takeaways"
        elif st.session_state.yt_active_tab == "topics" and sections["topics"]:
            active_content = format_topics(sections["topics"])
            active_heading = "Important Topics Covered"

        # Render dynamic block (if a sub-section is active)
        if st.session_state.yt_active_tab:
            st.markdown(f"### {active_heading}")
            st.markdown(f'<div class="summary-card">{active_content}</div>', unsafe_allow_html=True)

        # Recalculate analytics based on active content
        analytics = compute_analytics(data["transcript"], active_content)
        render_analytics_metrics(analytics)

        # Export active section or entire summary (entire summary preserves context)
        render_export_buttons(
            summary=summary,
            txt_filename="youtube_summary.txt",
            pdf_title=f"YouTube Summary: {data['title']}",
            key_suffix="yt",
        )


def _build_extra_instructions(custom_query: str) -> str:
    """Convert the user's natural-language query into a strict prompt directive."""
    if not custom_query or not custom_query.strip():
        return ""
    return (
        f"\n\n⚠️ CRITICAL FORMATTING REQUIREMENT — You MUST follow this exactly:\n"
        f"{custom_query.strip()}\n"
        f"Override any default formatting if needed to honour this instruction."
    )
