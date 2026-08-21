"""
services/export_service.py
Export summaries as TXT or PDF.
"""

from io import BytesIO


def export_txt(summary: str, filename: str = "summary.txt") -> bytes:
    """Return UTF-8 encoded bytes for a .txt download."""
    return summary.encode("utf-8")


def export_pdf(summary: str, title: str = "AI Summary") -> bytes:
    """
    Generate a clean PDF from the summary text using ReportLab.
    Returns bytes suitable for st.download_button.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2.5 * cm,
            rightMargin=2.5 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=18,
            textColor=colors.HexColor("#4F46E5"),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            spaceAfter=8,
            alignment=TA_LEFT,
        )

        story = [
            Paragraph(title, title_style),
            Spacer(1, 0.4 * cm),
        ]

        for line in summary.split("\n"):
            clean = line.strip()
            if clean:
                # Escape XML special chars
                clean = clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(clean, body_style))
            else:
                story.append(Spacer(1, 0.2 * cm))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        # Fallback: plain text PDF wrapper
        return export_txt(summary)
