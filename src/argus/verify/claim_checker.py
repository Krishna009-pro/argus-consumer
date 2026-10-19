from __future__ import annotations
from ..ledger import EvidenceLedger
from ..ingest.source_text import snippet_is_cached, snippet_contains_value

def check_claims(ledger: EvidenceLedger, ledger_ids: list[str], required_snippets: dict[str, str] | None = None) -> dict:
    required_snippets = required_snippets or {}
    issues, checked = [], 0
    for entry_id in ledger_ids:
        entry = ledger.get(entry_id)
        if entry is None:
            issues.append({"ledger_id": entry_id, "reason": "missing_ledger_entry"}); continue
        if not ledger.verify(entry):
            issues.append({"ledger_id": entry_id, "reason": "source_hash_missing_or_mismatch"}); continue
        if not snippet_is_cached(entry.cache_path, entry.snippet, entry.doc_page):
            issues.append({"ledger_id": entry_id, "reason": "snippet_not_found_in_cached_source"}); continue
        if not entry.source_url.startswith(("https://", "http://")) or entry.doc_page is None:
            issues.append({"ledger_id": entry_id, "reason": "source_url_or_page_missing"}); continue
        if not snippet_contains_value(entry.snippet, entry.value):
            issues.append({"ledger_id": entry_id, "reason": "snippet_does_not_contain_ledger_value"}); continue
        if required_snippets.get(entry_id) and required_snippets[entry_id] not in entry.snippet:
            issues.append({"ledger_id": entry_id, "reason": "snippet_does_not_support_claim"}); continue
        checked += 1
    return {"checked": checked, "issues": issues, "passed": not issues}
