"""
components/ui_helpers.py
Reusable Streamlit UI components shared across all pages.
"""

import streamlit as st
from services.export_service import export_txt, export_pdf


# ------------------------------------------------------------------ #
#  Sidebar: Summary settings + Custom Query                            #
# ------------------------------------------------------------------ #

def render_settings_sidebar(page_key: str = "default") -> tuple[str, str, str, str]:
    """
    Render length, style, strategy selectors, and a custom query box in the sidebar.
    Returns (length, style, strategy, custom_query).
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎛️ Summary Settings")

        length = st.select_slider(
            "Summary Length",
            options=["Short", "Medium", "Detailed"],
            value="Medium",
            key=f"global_length_{page_key}",
        )

        style = st.selectbox(
            "Summary Style",
            options=["Professional", "Academic", "Business", "Beginner Friendly"],
            key=f"global_style_{page_key}",
        )

        strategy_label = st.selectbox(
            "Summarization Strategy",
            options=[
                "Auto (Recommended)",
                "Stuff (Single request - best for free tier)",
                "Map-Reduce (Multi-request)",
                "Refine (Iterative/Multi-request)",
            ],
            help="For free tier API keys, 'Stuff' is highly recommended as it processes the entire content in a single request, avoiding rate limit errors.",
            key=f"global_strategy_{page_key}",
        )

        # Map to internal strategy key
        strategy = "auto"
        if "Stuff" in strategy_label:
            strategy = "stuff"
        elif "Map-Reduce" in strategy_label:
            strategy = "map_reduce"
        elif "Refine" in strategy_label:
            strategy = "refine"

        st.markdown("---")
        st.markdown("### 💬 Custom Instructions")
        st.caption("Tell AI exactly how to summarize — word count, sentences, bullets, etc.")

        custom_query = st.text_area(
            "Your instruction",
            placeholder=(
                "Examples:\n"
                "• Summarize in exactly 30 words\n"
                "• Give me 3 sentences only\n"
                "• List 5 key bullet points\n"
                "• Keep under 200 characters\n"
                "• Explain like I'm 10 years old"
            ),
            height=140,
            key=f"custom_query_{page_key}",
        )

    return length, style, strategy, custom_query


# ------------------------------------------------------------------ #
#  Strategy badge                                                       #
# ------------------------------------------------------------------ #

STRATEGY_COLORS = {
    "stuff": ("#06B6D4", "⚡ Stuff Chain"),
    "map_reduce": ("#7C3AED", "🗺️ Map-Reduce Chain"),
    "refine": ("#4F46E5", "🔄 Refine Chain"),
}


def render_strategy_badge(strategy: str, chunks: int):
    color, label = STRATEGY_COLORS.get(strategy, ("#64748B", strategy))
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin:10px 0;">
            <span style="
                background:{color};color:#fff;
                padding:4px 12px;border-radius:20px;
                font-size:0.82rem;font-weight:600;letter-spacing:0.5px;">
                {label}
            </span>
            <span style="color:#64748B;font-size:0.82rem;">
                {chunks} chunk{"s" if chunks != 1 else ""} processed
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ #
#  Custom query banner (shown when user has a custom instruction)      #
# ------------------------------------------------------------------ #

def render_custom_query_banner(custom_query: str):
    if custom_query and custom_query.strip():
        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,#EEF2FF,#F0FDF4);
                border:1.5px solid #A5B4FC;
                border-radius:10px;
                padding:10px 16px;
                margin:8px 0 14px 0;
                display:flex;
                align-items:center;
                gap:10px;
            ">
                <span style="font-size:1.2rem;">💬</span>
                <div>
                    <span style="font-size:0.78rem;color:#6366F1;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.8px;">
                        Custom Instruction Active
                    </span><br/>
                    <span style="font-size:0.9rem;color:#1E1B4B;font-weight:500;">
                        {custom_query.strip()}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------ #
#  Analytics metrics row                                               #
# ------------------------------------------------------------------ #

def render_analytics_metrics(analytics: dict):
    st.markdown("### 📊 Analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "📝 Summary Words",
        f"{analytics['summary_word_count']:,}",
        delta=f"-{analytics['original_word_count'] - analytics['summary_word_count']:,} from original",
        delta_color="normal",
    )
    c2.metric(
        "🔤 Summary Characters",
        f"{analytics['summary_char_count']:,}",
    )
    c3.metric(
        "⏱️ Reading Time",
        f"{analytics['summary_reading_time_min']} min",
        delta=f"was {analytics['original_reading_time_min']} min",
        delta_color="inverse",
    )
    c4.metric(
        "📉 Compression",
        f"{analytics['compression_ratio']}%",
        help="Percentage of the original content reduced in the summary.",
    )


# ------------------------------------------------------------------ #
#  Summary output display                                              #
# ------------------------------------------------------------------ #

def render_summary_output(summary: str):
    st.markdown("### 🤖 AI Generated Summary")
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.markdown(summary)
    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------ #
#  Rich Summary Layout (Generic for Website, Text, Doc)                #
# ------------------------------------------------------------------ #

def format_list_content(text: str) -> str:
    """Format bullet lists and topics."""
    lines = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
            
        if clean.startswith("### "):
            lines.append(clean)
            continue
        if clean.startswith("## "):
            lines.append(f"### {clean[3:].strip()}")
            continue
            
        is_bullet = False
        for prefix in ["- ", "* ", "• "]:
            if clean.startswith(prefix):
                lines.append(f"• {clean[len(prefix):].strip()}")
                is_bullet = True
                break
                
        if is_bullet:
            continue
            
        # Treat raw text lines as bullet points if they look like items
        if clean and clean[0].isdigit() and ". " in clean[:4]:
            parts = clean.split(". ", 1)
            if len(parts) > 1:
                lines.append(f"• {parts[1].strip()}")
                continue
        
        lines.append(f"• {clean}")
            
    return "\n\n".join(lines)


def parse_generic_sections(summary_text: str):
    sections = []
    current_title = "Summary"
    current_content = []
    
    for line in summary_text.splitlines():
        if line.startswith("## "):
            if current_content or len(sections) > 0:
                sections.append((current_title, "\n".join(current_content).strip()))
            current_title = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
            
    sections.append((current_title, "\n".join(current_content).strip()))
    
    # Filter out empty sections, and drop the initial dummy section if it's empty
    parsed = []
    for idx, (t, c) in enumerate(sections):
        if idx == 0 and t == "Summary" and not c:
            continue
        parsed.append((t, c))
        
    if not parsed:
        return ("Summary", summary_text.strip()), []
        
    return parsed[0], parsed[1:]


def render_rich_summary_dynamic(
    summary: str, 
    page_key: str, 
    original_text: str,
    txt_filename: str,
    pdf_title: str
):
    from utils.analytics import compute_analytics
    
    # 1. Parse sections
    main_sec, other_secs = parse_generic_sections(summary)
    
    # 2. Main Quick Summary
    st.markdown(f"### {main_sec[0]}")
    st.markdown(f'<div class="summary-card">{main_sec[1]}</div>', unsafe_allow_html=True)
    
    active_tab_key = f"{page_key}_active_tab"
    
    # 3. Explore Further
    if other_secs:
        st.markdown("### 🔍 Explore Further")
        
        # Limit to 3 or 4 columns max for better fit, wrap if needed
        cols = st.columns(len(other_secs))
        for i, (title, content) in enumerate(other_secs):
            with cols[i % len(cols)]: # Just in case it exceeds
                tab_id = f"tab_{i}"
                btn_type = "primary" if st.session_state.get(active_tab_key) == tab_id else "secondary"
                if st.button(title, type=btn_type, use_container_width=True, key=f"btn_{page_key}_{i}"):
                    st.session_state[active_tab_key] = tab_id
                    st.rerun()
                    
    # 4. Active Tab Content & Analytics
    active_tab_id = st.session_state.get(active_tab_key)
    active_content = main_sec[1]
    
    if active_tab_id is not None:
        try:
            idx = int(active_tab_id.split("_")[1])
            active_title, raw_content = other_secs[idx]
            
            # Format bullets if needed
            if any(k in active_title.lower() for k in ["takeaway", "topic", "insight", "bullet", "finding", "keyword", "action", "recommendation"]):
                formatted_content = format_list_content(raw_content)
            else:
                formatted_content = raw_content
                
            st.markdown(f"### {active_title}")
            st.markdown(f'<div class="summary-card">{formatted_content}</div>', unsafe_allow_html=True)
            active_content = formatted_content
        except (ValueError, IndexError):
            pass
            
    # Analytics
    analytics = compute_analytics(original_text, active_content)
    render_analytics_metrics(analytics)
    
    # Export
    render_export_buttons(
        summary=summary,
        txt_filename=txt_filename,
        pdf_title=pdf_title,
        key_suffix=page_key
    )


# ------------------------------------------------------------------ #
#  Export buttons                                                      #
# ------------------------------------------------------------------ #

def render_export_buttons(summary: str, txt_filename: str, pdf_title: str, key_suffix: str = ""):
    st.markdown("### 📥 Export Summary")
    col1, col2 = st.columns(2)

    # Unique keys prevent duplicate-widget errors when the same page reruns
    uid = key_suffix or txt_filename.replace(".", "_").replace(" ", "_")

    with col1:
        st.download_button(
            label="⬇️ Download as TXT",
            data=export_txt(summary),
            file_name=txt_filename,
            mime="text/plain",
            use_container_width=True,
            key=f"dl_txt_{uid}",
        )

    with col2:
        pdf_bytes = export_pdf(summary, title=pdf_title)
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_bytes,
            file_name=txt_filename.replace(".txt", ".pdf"),
            mime="application/pdf",
            use_container_width=True,
            key=f"dl_pdf_{uid}",
        )
