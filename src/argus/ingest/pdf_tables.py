"""Conservative extraction of financial-statement rows from PDF text.

Only rows on pages with a dated financial-statement header are proposed. When
the header has a Note column, the extractor takes values from the rightmost
dated financial columns, so a note reference cannot become a financial value.
Every result remains a candidate for human review.
"""
from __future__ import annotations
import re
from pathlib import Path

ROW_LABELS = {
    "trade_receivables": re.compile(r"^\s*(?:\([a-z0-9]+\)\s*)?(?:\([ivxlcdm]+\)\s*)?trade\s+(?:receivables|debtors)\b", re.I),
    "inventory": re.compile(r"^\s*(?:\([a-z0-9]+\)\s*)?inventories\b", re.I),
    "revenue": re.compile(r"^\s*(?:[ivxlcdm]+\s+)?revenue\s+from\s+operations\b", re.I),
    "operating_cash_flow": re.compile(
        r"^\s*net\s+cash\s+(?:from|used\s+in)\s+operating\s+activities\b", re.I),
    "ebitda": re.compile(r"^\s*EBITDA\b", re.I),
}
NUMBER = re.compile(r"\(?-?\d[\d,]*(?:\.\d+)?\)?")
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")


def _dated_statement_header(lines: list[str]) -> tuple[str, list[str]] | None:
    # Reports commonly split the statement title, date and column headings
    # across several extracted text lines.
    # Search short adjacent windows and retain the two dated value columns.
    for start in range(len(lines)):
        for end in range(start + 1, min(len(lines), start + 6) + 1):
            window = lines[start:end]
            normalized = re.sub(r"(?i)\by\s+ear\b", "year", " ".join(window))
            years = list(dict.fromkeys(YEAR.findall(normalized)))
            if (len(years) >= 2
                    and re.search(r"\b(?:as\s+at|year\s+ended)\b", normalized, re.I)
                    and re.search(r"\b(?:note|particulars|for\s+the\s+year\s+ended)\b", normalized, re.I)):
                return " | ".join(part.strip() for part in window), years[-2:]
    return None


def _number(token: str) -> float:
    negative = token.startswith("(") and token.endswith(")")
    value = float(token.strip("()").replace(",", ""))
    return -value if negative else value


def _pdfplumber_texts(path: str | Path):
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("Install the optional ingestion dependencies with pip install -e .[ingest].") from exc
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            try:
                yield page.extract_text() or ""
            finally:
                # pdfplumber caches each page's layout objects. Clear them as
                # soon as the caller has processed the page to keep RSS bounded.
                close = getattr(page, "close", None)
                if close is not None:
                    close()


def _page_texts(path: str | Path):
    """Use pypdf for ordinary PDFs and stream large reports through pdfplumber."""
    source = Path(path)
    # pypdf can retain very large page/content object graphs for long annual
    # reports. Route those directly to the streaming reader to bound memory.
    if source.is_file() and source.stat().st_size > 25 * 1024 * 1024:
        return _pdfplumber_texts(path)
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        # Materialize only the small-file text pass so a failed pypdf parse can
        # safely restart with pdfplumber without emitting duplicate proposals.
        return iter([page.extract_text() or "" for page in reader.pages])
    except Exception as primary_error:
        try:
            return _pdfplumber_texts(path)
        except Exception as fallback_error:
            raise RuntimeError(
                f"Could not extract PDF text with pypdf ({primary_error}) or pdfplumber ({fallback_error})."
            ) from fallback_error


def extract(path: str | Path) -> list[dict]:
    results: list[dict] = []
    for page_number, text in enumerate(_page_texts(path), 1):
        lines = text.splitlines()
        header = _dated_statement_header(lines)
        if header is None:
            continue
        header_line, years = header
        page_intro = " ".join(lines[:18]).casefold()
        if "balance sheet" in page_intro:
            allowed_metrics = {"trade_receivables", "inventory"}
        elif "statement of profit and loss" in page_intro:
            allowed_metrics = {"revenue", "ebitda"}
        elif "statement of cash flows" in page_intro or "cash flow statement" in page_intro:
            allowed_metrics = {"operating_cash_flow"}
        else:
            # Dated ratio tables and narrative pages are not primary statements.
            continue
        column_count = len(years)
        footer = next((i for i, line in enumerate(lines)
                       if "the accompanying notes" in line.casefold()), len(lines))
        for line in lines[:footer]:
            for metric, label in ROW_LABELS.items():
                if metric not in allowed_metrics:
                    continue
                match = label.match(line)
                if not match:
                    continue
                # Financial values occupy the rightmost columns labelled by
                # years; earlier numeric tokens may be the Note reference.
                tokens = NUMBER.findall(line[match.end():])
                if len(tokens) < column_count:
                    continue
                selected = tokens[-column_count:]
                for token, year in zip(selected, years[-column_count:]):
                    value = _number(token)
                    results.append({
                        "metric": metric,
                        "value": value,
                        "period_header": year,
                        "page": page_number,
                        "snippet": line.strip(),
                        "warning": (
                            "Machine-extracted financial-statement candidate; verify the value, "
                            "column header, units, reporting period, basis and scope against the PDF."
                        ),
                        "column_header": header_line.strip(),
                    })
    return results
