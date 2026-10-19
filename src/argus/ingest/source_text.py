"""Decode cached source text for literal snippet and value verification."""
from __future__ import annotations
import math, re
from pathlib import Path

def extract_text(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install `.[ingest]` to verify PDF evidence snippets.") from exc
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8-sig")

def snippet_is_cached(path: str | Path | None, snippet: str, page: int | None = None) -> bool:
    if not path or not Path(path).is_file(): return False
    try:
        source = Path(path)
        if source.suffix.lower() == ".pdf" and page is not None:
            if page < 1: return False
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(source))
                if page <= len(reader.pages) and snippet in (reader.pages[page - 1].extract_text() or ""):
                    return True
            except Exception:
                pass
            # Keep provenance checks usable for valid PDFs that pypdf cannot
            # parse; compare normalized extracted text from the fallback reader.
            import pdfplumber
            with pdfplumber.open(str(source)) as pdf:
                if page > len(pdf.pages): return False
                normalize = lambda value: " ".join(value.split())
                return normalize(snippet) in normalize(pdf.pages[page - 1].extract_text() or "")
        return snippet in extract_text(source)
    except Exception: return False

def snippet_contains_value(snippet: str, value: float, tolerance: float = 0.005) -> bool:
    tokens = [float(token.replace(",", "")) for token in re.findall(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?", snippet)]
    return any(math.isclose(number, value, rel_tol=tolerance, abs_tol=0.01) for number in tokens)
