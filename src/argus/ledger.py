"""Append-only evidence ledger backed by cached public source files."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Iterable
from .schemas import LedgerEntry

class EvidenceLedger:
    def __init__(self, path: str | Path = "data/ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sha256(path: str | Path) -> str:
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def append(self, entry: LedgerEntry) -> None:
        if not entry.verified or not entry.verified_by or not entry.verified_at:
            raise ValueError("Only manually reviewed, verified observations may enter the ledger.")
        if not entry.company or not entry.period or not entry.unit or not entry.period_type or not entry.currency:
            raise ValueError("Company, disclosed period, period type, unit and currency (or N/A) are required for ledger observations.")
        if not entry.cache_path or not Path(entry.cache_path).is_file():
            raise ValueError("A present cached source file is required for every ledger observation.")
        if entry.source_type == "filing" and entry.doc_page is None:
            raise ValueError("A filing observation must identify its source page.")
        if not entry.source_url.startswith(("https://", "http://")) or not entry.snippet:
            raise ValueError("A public source URL and exact supporting snippet are required.")
        if entry.cache_path and self.sha256(entry.cache_path) != entry.source_sha256:
            raise ValueError(f"Cached source hash mismatch: {entry.cache_path}")
        from .ingest.source_text import snippet_is_cached, snippet_contains_value
        if not snippet_is_cached(entry.cache_path, entry.snippet, entry.doc_page):
            raise ValueError("The supporting snippet is not present verbatim in the cached source.")
        if not snippet_contains_value(entry.snippet, entry.value):
            raise ValueError("The exact source snippet does not contain the ledger value.")
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(entry.model_dump_json() + "\n")

    def entries(self) -> list[LedgerEntry]:
        if not self.path.exists():
            return []
        return [LedgerEntry.model_validate_json(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def get(self, entry_id: str) -> LedgerEntry | None:
        return next((entry for entry in self.entries() if entry.id == entry_id), None)

    def verify(self, entry: LedgerEntry) -> bool:
        return bool(entry.cache_path and Path(entry.cache_path).is_file() and self.sha256(entry.cache_path) == entry.source_sha256)

    def next_id(self) -> str:
        return f"L{len(self.entries()) + 1:04d}"

    def verified_entries(self, company: str | None = None) -> list[LedgerEntry]:
        rows = [e for e in self.entries() if e.verified and e.verified_by and e.verified_at and self.verify(e)]
        return rows if company is None else [e for e in rows if e.company and e.company.casefold() == company.casefold()]

def verify_entries(entries: Iterable[LedgerEntry]) -> bool:
    return all(e.cache_path and Path(e.cache_path).is_file() and EvidenceLedger.sha256(e.cache_path) == e.source_sha256 for e in entries)
