"""Readable, source-linked PDF reports for a validated ARGUS dossier."""
from __future__ import annotations

import io
import unicodedata
from collections import defaultdict
from datetime import date
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..schemas import Dossier


INK = colors.HexColor("#18324A")
TEAL = colors.HexColor("#117C78")
PALE_TEAL = colors.HexColor("#E8F4F2")
PALE_AMBER = colors.HexColor("#FFF4DE")
PALE_RED = colors.HexColor("#FCEBE8")
PALE_BLUE = colors.HexColor("#EEF3F8")
MUTED = colors.HexColor("#586B7A")
RULE = colors.HexColor("#D8E0E7")
WHITE = colors.white


def _field(item, key: str, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _plain(value) -> str:
    """Normalize report text to portable, readable built-in PDF font characters."""
    text = str(value if value is not None else "")
    for old, new in {
        "₹": "INR ", "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "−": "-", "…": "...", "·": " | ",
        "×": "x", "≥": ">=", "≤": "<=", "•": "-",
    }.items():
        text = text.replace(old, new)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _human_label(value) -> str:
    """Render internal snake-case scope labels as words in the reader-facing report."""
    text = _plain(value).replace("_", " ").replace("demeger", "demerger")
    words = text.split()
    acronyms = {"fy", "inr"}
    return " ".join(word.upper() if word.casefold() in acronyms else word.capitalize() for word in words)


def _source_label(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.removeprefix("www.")
    filename = parsed.path.rstrip("/").rsplit("/", 1)[-1]
    return _plain(f"{host} / {filename}" if filename else host or "Open public report")


def _p(value, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_plain(value)).replace("\n", "<br/>"), style)


def _rich(value: str, style: ParagraphStyle) -> Paragraph:
    """Build Paragraph markup assembled from escaped dynamic text and fixed tags."""
    return Paragraph(value, style)


def _state_label(state: str) -> str:
    labels = {
        "no_reliable_finding": "No reliable finding",
        "explained": "Candidate explained",
        "unexplained": "Candidate needs review",
        "rejected": "Finding rejected",
        "abstained": "Analysis abstained",
    }
    return labels.get(state, state.replace("_", " ").title() or "Unknown")


def _format_number(value, places: int = 2) -> str:
    if value is None:
        return "Not available"
    try:
        return f"{float(value):,.{places}f}"
    except (TypeError, ValueError):
        return _plain(value)


def _format_unit(unit: str | None) -> str:
    if not unit:
        return ""
    return {
        "INR_crore": "INR crore",
        "INR_cr": "INR crore",
        "pct": "%",
        "days": "days",
    }.get(unit, unit.replace("_", " "))


def _period_metadata_warnings(entries: list) -> list[str]:
    grouped: dict[tuple, set[str]] = defaultdict(set)
    for entry in entries:
        start = _field(entry, "period_start")
        end = _field(entry, "period_end")
        label = _field(entry, "period")
        if start and end and label:
            key = (
                str(start), str(end), _field(entry, "company"),
                _field(entry, "consolidation_basis"), _field(entry, "reporting_scope"),
                _field(entry, "comparability_cohort"),
            )
            grouped[key].add(str(label))
    warnings = []
    for (start, end, _company, _basis, _scope, _cohort), labels in grouped.items():
        if len(labels) > 1:
            warnings.append(
                f"Different financial-period labels ({', '.join(sorted(labels))}) share the same stored date range "
                f"({start} to {end}). Confirm the period dates against the source statements before relying on this sequence."
            )
    return warnings


def _reason_explanation(reason: str) -> str:
    lowered = reason.casefold()
    if "six" in lowered:
        return "This specific measure does not have enough usable comparable observations. Other metrics or reporting scopes do not count toward its history."
    if "denominator" in lowered or "period day" in lowered:
        return "The calculation needs a positive, same-unit denominator and a known number of days for the reported period."
    if "peer" in lowered:
        return "There are not enough compatible peer observations for a fair comparison."
    return "The required verified inputs or comparability checks were unavailable, so this measure was left untested."


def _get_styles():
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle("ArgusEyebrow", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=TEAL, spaceAfter=7),
        "title": ParagraphStyle("ArgusTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=26, leading=31, alignment=TA_LEFT, textColor=INK, spaceAfter=6),
        "subtitle": ParagraphStyle("ArgusSubtitle", parent=base["BodyText"], fontName="Helvetica", fontSize=11, leading=15, textColor=MUTED, spaceAfter=14),
        "h1": ParagraphStyle("ArgusH1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=INK, spaceBefore=5, spaceAfter=9, keepWithNext=True),
        "h2": ParagraphStyle("ArgusH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("ArgusBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.3, textColor=INK, spaceAfter=6),
        "small": ParagraphStyle("ArgusSmall", parent=base["BodyText"], fontName="Helvetica", fontSize=7.4, leading=9.5, textColor=MUTED),
        "table": ParagraphStyle("ArgusTable", parent=base["BodyText"], fontName="Helvetica", fontSize=7.8, leading=10, textColor=INK),
        "table_small": ParagraphStyle("ArgusTableSmall", parent=base["BodyText"], fontName="Helvetica", fontSize=6.8, leading=8.5, textColor=INK),
        "table_header": ParagraphStyle("ArgusTableHeader", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.4, leading=9, textColor=WHITE),
        "callout": ParagraphStyle("ArgusCallout", parent=base["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13.4, textColor=INK, spaceAfter=0),
        "metric_value": ParagraphStyle("ArgusMetricValue", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK, alignment=TA_CENTER),
        "metric_label": ParagraphStyle("ArgusMetricLabel", parent=base["BodyText"], fontName="Helvetica", fontSize=7.5, leading=10, textColor=MUTED, alignment=TA_CENTER),
        "center": ParagraphStyle("ArgusCenter", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=10, textColor=INK, alignment=TA_CENTER),
    }


def _make_table(rows, widths, *, header=True, small=False, repeat=1):
    styles = _get_styles()
    header_style = styles["table_header"]
    body_style = styles["table_small"] if small else styles["table"]
    data = []
    for row_index, row in enumerate(rows):
        style = header_style if header and row_index == 0 else body_style
        data.append([cell if isinstance(cell, (Paragraph, Table)) else _p(cell, style) for cell in row])
    table = LongTable(data, colWidths=widths, repeatRows=repeat if header else 0, hAlign="LEFT", splitByRow=1)
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, INK),
        ])
    for row_index in range(1 if header else 0, len(data)):
        if row_index % 2 == 0:
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), PALE_BLUE))
    table.setStyle(TableStyle(commands))
    return table


def _panel_and_angle_rows(analysis: dict | None):
    panels = (analysis or {}).get("panels", [])
    panel_rows = []
    angle_rows = []
    reason_groups: dict[str, dict] = {}
    tested_count = 0
    abstained_count = 0
    for index, result in enumerate(panels, start=1):
        panel = result.get("panel", {})
        periods = panel.get("periods", [])
        labels = [str(item.get("period", "")) for item in periods]
        tested = sum(angle.get("status") == "tested" for angle in result.get("angles", {}).values())
        abstained = sum(angle.get("status") == "abstained" for angle in result.get("angles", {}).values())
        tested_count += tested
        abstained_count += abstained
        panel_rows.append([
            str(index), _human_label(panel.get("comparability_cohort") or "Unlabeled"),
            _human_label(panel.get("consolidation_basis") or "Unknown"), _human_label(panel.get("reporting_scope") or "Not recorded"),
            f"{labels[0]} to {labels[-1]}" if labels else "No periods",
            str(len(periods)), f"{tested} tested / {abstained} abstained",
        ])
        for name, angle in result.get("angles", {}).items():
            status = angle.get("status", "unknown")
            if status == "abstained":
                abstention = angle.get("abstain_reason") or "Required inputs unavailable."
                record = reason_groups.setdefault(abstention, {"count": 0, "angles": set()})
                record["count"] += 1
                record["angles"].add(name.replace("_", " "))
            if status != "tested":
                continue
            values = angle.get("reported", [])
            periods_for_angle = angle.get("periods", [])
            low_values = angle.get("expected_low", [])
            high_values = angle.get("expected_high", [])
            flags = angle.get("gap_flags", [])
            indexes = [i for i, value in enumerate(values) if value is not None]
            if not indexes:
                continue
            latest = indexes[-1]
            value = values[latest]
            low = low_values[latest] if latest < len(low_values) else None
            high = high_values[latest] if latest < len(high_values) else None
            latest_flag = flags[latest] if latest < len(flags) else None
            trailing_run = 0
            for flag in reversed(flags[:latest + 1]):
                if not flag:
                    break
                trailing_run += 1
            unit = "days" if name.endswith("_days") else "ratio"
            if low is None or high is None:
                comparison = "No historical band for this period"
            elif latest_flag:
                comparison = f"Outside band; latest consecutive run: {trailing_run}"
            else:
                comparison = "Within historical band"
            ids_by_period = angle.get("ledger_ids_by_period", [])
            ids = ids_by_period[latest] if latest < len(ids_by_period) else []
            scope = " | ".join(_human_label(panel.get(key) or "") for key in ("comparability_cohort", "consolidation_basis", "reporting_scope")).strip(" |")
            angle_rows.append({
                "panel": scope,
                "angle": name.replace("_", " ").title(),
                "period": periods_for_angle[latest] if latest < len(periods_for_angle) else "Unknown",
                "value": value,
                "low": low,
                "high": high,
                "unit": unit,
                "comparison": comparison,
                "ledger_ids": ids,
                "denominator": angle.get("metadata", {}).get("denominator"),
            })
    return panel_rows, angle_rows, reason_groups, tested_count, abstained_count


def _source_register(entries: list):
    source_by_hash: dict[str, dict] = {}
    for entry in entries:
        digest = _field(entry, "source_sha256", "") or ""
        if not digest:
            continue
        if digest not in source_by_hash:
            source_by_hash[digest] = {
                "id": f"D{len(source_by_hash) + 1:02d}",
                "url": _field(entry, "source_url", ""),
                "hash": digest,
            }
    return source_by_hash


def _footer(company: str):
    def draw(canvas, doc):
        canvas.saveState()
        width, _height = letter
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(0.62 * inch, 0.52 * inch, width - 0.62 * inch, 0.52 * inch)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.65 * inch, 0.34 * inch, f"ARGUS | {company} | Evidence-led screening, not investment advice")
        canvas.drawRightString(width - 0.65 * inch, 0.34 * inch, f"Page {doc.page}")
        canvas.restoreState()
    return draw


def build_pdf(dossier: Dossier, ledger_entries: list | None = None, analysis: dict | None = None) -> bytes:
    """Create a plain-language PDF summary with angle results and source provenance.

    ``ledger_entries`` and ``analysis`` are optional for compatibility with existing
    callers. They allow the report to explain why an angle was tested or abstained
    and to connect source-backed observations to their original filing pages.
    """
    buffer = io.BytesIO()
    styles = _get_styles()
    company = _plain(dossier.company)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.72 * inch,
        title=f"ARGUS company financial screen - {company}",
        author="ARGUS Consumer Intelligence",
    )
    verified_ids = set(dossier.evidence or [])
    entries = [
        entry for entry in (ledger_entries or [])
        if _field(entry, "id") in verified_ids and _field(entry, "verified", True)
    ]
    entries.sort(key=lambda item: (
        str(_field(item, "period_end", "")),
        str(_field(item, "period", "")),
        str(_field(item, "metric", "")),
        str(_field(item, "id", "")),
    ))
    validation = dossier.validation or {}
    state = str(validation.get("state", "unknown"))
    status = _state_label(state)
    panels, tested_results, reason_groups, tested_count, abstained_count = _panel_and_angle_rows(analysis)
    candidate_count = len(validation.get("generated_candidates") or validation.get("candidates") or [])
    rejected_count = len(validation.get("rejected_findings") or [])
    source_register = _source_register(entries)
    metadata_warnings = _period_metadata_warnings(entries)

    story = []
    story.append(_p("ARGUS | COMPANY FINANCIAL SCREEN", styles["eyebrow"]))
    story.append(_p(company, styles["title"]))
    story.append(_p(f"Plain-language analysis summary | Prepared {date.today().strftime('%d %B %Y')}", styles["subtitle"]))

    status_color = PALE_TEAL if state == "explained" else PALE_AMBER
    status_content = (
        f"<b>RUN RESULT: {escape(_plain(status).upper())}</b><br/><br/>"
        f"{escape(_plain(dossier.discovery))}"
    )
    status_table = Table(
        [[_rich(status_content, styles["callout"])]],
        colWidths=[7.25 * inch],
    )
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), status_color),
        ("BOX", (0, 0), (-1, -1), 0.8, TEAL if state == "explained" else colors.HexColor("#BE8A22")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    story.extend([status_table, Spacer(1, 13)])

    story.append(_p("What is this PDF for?", styles["h1"]))
    story.append(_p(
        "ARGUS checks whether verified financial measures look unusual compared with a company's own comparable history and, when enough matching data exists, similar companies. "
        "It then checks whether a gap persists and whether the evidence is strong enough to report. This PDF summarizes that screening run and links the input observations back to public filings.",
        styles["body"],
    ))
    story.append(_p("How to understand the result", styles["h2"]))
    story.append(_rich(
        "<b>No reliable finding</b> means this run did not produce a candidate that passed its screening and evidence requirements. It does not prove that the company has no risk. "
        "<b>Abstained</b> means a calculation could not be made responsibly because required data were missing, too short, or not comparable. "
        "A <b>tested measure</b> is a calculation, not a discovery or an allegation.",
        styles["body"],
    ))

    summary_values = [
        (str(validation.get("verified_ledger_entries", len(entries))), "Verified observations"),
        (str(validation.get("panel_count", len(panels))), "Comparable data panels"),
        (str(candidate_count), "Generated candidates"),
        (str(rejected_count), "Rejected candidates"),
    ]
    summary_cells = [[_p(value, styles["metric_value"]) for value, _label in summary_values],
                     [_p(label, styles["metric_label"]) for _value, label in summary_values]]
    summary_table = Table(summary_cells, colWidths=[1.81 * inch] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([Spacer(1, 3), summary_table, Spacer(1, 10)])

    story.append(_p("What ARGUS checked", styles["h2"]))
    story.append(_p(
        f"This run contains {tested_count} tested angle-panel checks and {abstained_count} abstentions. "
        "A panel is a set of observations kept together because their period, currency, statement basis, and reporting scope can be compared. "
        "ARGUS keeps different scopes separate rather than blending them to make a longer history.",
        styles["body"],
    ))
    story.append(_p("Terms in everyday language", styles["h2"]))
    glossary_rows = [
        ["Term", "Meaning"],
        ["Verified observation", "A reported value checked against its cached source document and page. It is an input, not an ARGUS conclusion."],
        ["Historical comparison band", "A range calculated from prior comparable observations. It is not a forecast or a target."],
        ["Outside the band", "A screening flag that needs context. One flagged period alone does not establish a persistent pattern."],
        ["Candidate", "A possible pattern sent to further checks. It is not published as a finding unless the validation gate passes."],
        ["Abstention", "ARGUS withheld the calculation or comparison because evidence was missing or could not safely be matched."],
    ]
    story.extend([_make_table(glossary_rows, [1.55 * inch, 5.7 * inch]), Spacer(1, 8)])

    story.append(PageBreak())
    story.append(_p("Screen results", styles["h1"]))
    story.append(_p(
        "The table shows the latest usable value for each angle that the saved analysis marked as tested. "
        "Values are code-calculated from the linked verified observations; they are not quoted company disclosures.",
        styles["body"],
    ))
    if tested_results:
        rows = [["Measure and data scope", "Latest period", "Calculated value", "Historical band", "Screen status"]]
        for result in tested_results:
            refs = ", ".join(result["ledger_ids"]) or "No IDs recorded"
            band = "Not available" if result["low"] is None or result["high"] is None else f"{_format_number(result['low'])} to {_format_number(result['high'])} {result['unit']}"
            rows.append([
                _rich(
                    f"{escape(_plain(result['angle']))}<br/><font size='6.8' color='#586B7A'>"
                    f"{escape(_plain(result['panel']))}<br/>Evidence: {escape(_plain(refs))}</font>",
                    styles["table_small"],
                ),
                result["period"],
                f"{_format_number(result['value'])} {result['unit']}",
                band,
                result["comparison"],
            ])
        story.append(_make_table(rows, [1.75 * inch, 0.74 * inch, 1.05 * inch, 1.3 * inch, 2.4 * inch], small=True))
        story.append(Spacer(1, 8))
        story.append(_p("How to read those measures", styles["h2"]))
        glossary = {
            "Receivable Days": "An approximate number of days of revenue represented by unpaid customer invoices. Higher values can mean cash is collected more slowly; context is needed.",
            "Inventory Days": "An approximate number of days of activity represented by inventory. The report notes which disclosed denominator was used; a revenue denominator is a rough proxy when cost of goods is unavailable.",
        }
        for result in tested_results:
            description = glossary.get(result["angle"], "A code-calculated indicator based on the cited verified observations.")
            if result.get("denominator"):
                description += f" Denominator recorded by the analysis: {result['denominator'].replace('_', ' ')}."
            story.append(_rich(f"<b>{escape(_plain(result['angle']))}:</b> {escape(_plain(description))}", styles["body"]))
        story.append(_p(
            "An outside-band value is only a screen signal. ARGUS also considers whether it persists and whether comparable peer evidence and other validation checks are available.",
            styles["body"],
        ))
    else:
        story.append(_p("No angle had a usable tested value in this run.", styles["body"]))

    if reason_groups:
        story.append(_p("Why checks were not completed", styles["h2"]))
        reason_rows = [["Recorded reason", "Plain-language explanation", "Checks"]]
        for reason, details in sorted(reason_groups.items(), key=lambda item: (-item[1]["count"], item[0])):
            reason_rows.append([
                reason,
                _reason_explanation(reason),
                f"{details['count']} ({', '.join(sorted(details['angles']))})",
            ])
        story.append(_make_table(reason_rows, [2.25 * inch, 3.75 * inch, 1.24 * inch], small=True))

    story.append(PageBreak())
    story.append(_p("Panel coverage and data limits", styles["h1"]))
    story.append(_p(
        "Panels are analyzed separately to avoid mixing different reporting periods or business scopes. A large panel count can therefore mean the filing contains several non-comparable groups, not that the history is complete.",
        styles["body"],
    ))
    if panels:
        panel_table = [["#", "Cohort", "Basis", "Reporting scope", "Stored periods", "N", "Angle coverage"]]
        panel_table.extend(panels)
        story.append(_make_table(panel_table, [0.25 * inch, 1.3 * inch, 0.64 * inch, 1.12 * inch, 1.13 * inch, 0.25 * inch, 1.95 * inch], small=True))
    else:
        story.append(_p("No analysis panel artifact was available for this export.", styles["body"]))

    if metadata_warnings:
        warning_rows = [[_p("Period-date review needed", styles["table_header"])]]
        warning_rows.extend([[_p(item, styles["callout"])] for item in metadata_warnings])
        warning_table = Table(warning_rows, colWidths=[6.64 * inch])
        warning_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#9B5D16")),
            ("BACKGROUND", (0, 1), (-1, -1), PALE_AMBER),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BE8A22")),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.extend([Spacer(1, 8), warning_table])

    story.append(_p("What the current outcome does and does not say", styles["h2"]))
    story.append(_p(
        "The system did not publish a finding. This means the available data did not produce a pattern that met the existing deterministic screening rules. "
        "It is not a conclusion that the company is healthy or unhealthy, and it is not an allegation or investment recommendation.",
        styles["body"],
    ))
    if dossier.not_tested:
        # Convert repeated panel-by-panel abstentions into a small, readable set of unique notes.
        unique_notes = list(dict.fromkeys(_plain(item).split(": ", 1)[-1] for item in dossier.not_tested))
        for note in unique_notes[:8]:
            story.append(_p(f"- {note}", styles["small"]))
        if len(unique_notes) > 8:
            story.append(_p(f"- {len(unique_notes) - 8} additional distinct notes are retained in the JSON dossier.", styles["small"]))

    story.append(PageBreak())
    story.append(_p("Verified evidence register", styles["h1"]))
    story.append(_p(
        "Each observation below has a ledger ID used by the calculations. Follow the document reference to the public filing and the PDF page to check the original table. "
        "The cached SHA-256 digest identifies the exact file used for this run.",
        styles["body"],
    ))
    if entries:
        rows = [["Ledger ID", "Financial item", "Reported value", "Period", "Basis / scope", "Source page"]]
        source_for_hash = source_register
        for entry in entries:
            digest = _field(entry, "source_sha256", "") or ""
            source = source_for_hash.get(digest, {})
            url = _field(entry, "source_url", "") or ""
            doc_ref = source.get("id", "Unknown")
            page = _field(entry, "doc_page")
            source_cell = f"{escape(_plain(doc_ref))}<br/>p. {escape(_plain(page if page else 'not recorded'))}"
            if url:
                safe_url = escape(_plain(url), {"'": "&#x27;"})
                source_cell += f"<br/><link href='{safe_url}' color='#117C78'>Open PDF</link>"
            rows.append([
                _field(entry, "id", ""),
                str(_field(entry, "metric", "")).replace("_", " ").title(),
                f"{_format_number(_field(entry, 'value'))} {_format_unit(_field(entry, 'unit'))}",
                _field(entry, "period", "Unknown"),
                " / ".join(str(value) for value in (
                    _human_label(_field(entry, "consolidation_basis", "unknown")),
                    _human_label(_field(entry, "reporting_scope", "scope not recorded")),
                ) if value),
                _rich(source_cell, styles["table_small"]),
            ])
        # Source links are trusted public URLs from the already reviewed ledger.
        evidence_rows = [[_p(cell, styles["table_header"]) if isinstance(cell, str) else cell for cell in rows[0]]]
        evidence_rows.extend([
            [_p(cell, styles["table_small"]) if isinstance(cell, str) else cell for cell in row]
            for row in rows[1:]
        ])
        evidence_table = LongTable(evidence_rows, colWidths=[0.58 * inch, 1.08 * inch, 1.05 * inch, 0.66 * inch, 2.04 * inch, 0.91 * inch], repeatRows=1, hAlign="LEFT", splitByRow=1)
        evidence_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
        ] + [("BACKGROUND", (0, i), (-1, i), PALE_BLUE) for i in range(2, len(evidence_rows), 2)]))
        story.extend([evidence_table, Spacer(1, 12)])

        story.append(_p("Source file fingerprints", styles["h2"]))
        source_rows = [["Document", "Public source", "Cached SHA-256"]]
        for source in source_register.values():
            safe_url = escape(_plain(source.get("url", "")), {"'": "&#x27;"})
            link_label = escape(_source_label(source.get("url", "")))
            link = _rich(f"<link href='{safe_url}' color='#117C78'>{link_label}</link>", styles["table_small"]) if source.get("url") else _p("URL not recorded", styles["table_small"])
            source_rows.append([source["id"], link, source["hash"]])
        source_table_data = [[_p(cell, styles["table_header"]) if isinstance(cell, str) else cell for cell in source_rows[0]]]
        source_table_data.extend([[_p(str(cell), styles["table_small"]) if isinstance(cell, str) else cell for cell in row] for row in source_rows[1:]])
        source_table = LongTable(source_table_data, colWidths=[0.72 * inch, 2.05 * inch, 3.55 * inch], repeatRows=1, hAlign="LEFT", splitByRow=1)
        source_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
        ] + [("BACKGROUND", (0, i), (-1, i), PALE_BLUE) for i in range(2, len(source_table_data), 2)]))
        story.append(source_table)
    else:
        story.append(_p("No verified ledger entries were linked to this dossier at export time.", styles["body"]))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
    story.append(Spacer(1, 7))
    story.append(_p(
        "Prepared from the saved ARGUS dossier, analysis artifact, and verified local evidence ledger. "
        "No numbers in this report are generated by a language model. Missing or incomparable inputs remain unavailable.",
        styles["small"],
    ))

    footer = _footer(company)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
