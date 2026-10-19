"""PDF export for a validated dossier, used by both CLI and dashboard."""
from __future__ import annotations
import io
import unicodedata
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from ..schemas import Dossier
from .dossier import render


def build_pdf(dossier: Dossier) -> bytes:
    """Render Markdown dossier text into a portable, word-wrapped PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.7*inch,
                            leftMargin=0.7*inch, topMargin=0.65*inch, bottomMargin=0.65*inch)
    styles = getSampleStyleSheet()
    story = []
    for line in render(dossier).splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 5))
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        text = stripped[level:].strip() if level else stripped
        text = text.replace("**", "").replace("`", "")
        # Helvetica's built-in encoding is portable; normalize typographic punctuation.
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        if level == 1: style = styles["Title"]
        elif level == 2: style = styles["Heading2"]
        elif level >= 3: style = styles["Heading3"]
        else: style = styles["BodyText"]
        story.append(Paragraph(escape(text), style))
        story.append(Spacer(1, 3))
    doc.build(story)
    return buffer.getvalue()
