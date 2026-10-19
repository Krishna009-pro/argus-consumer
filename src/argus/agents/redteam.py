"""Evidence-checked red-team alternatives for deterministic candidates.

Language models may suggest alternatives, but only a reviewed, hash-matched
cached source can move a check out of ``not_tested``. A benign share is
calculated from explicit source-backed amounts and the deterministic gap.
"""
from __future__ import annotations

import math
from pathlib import Path

from ..ingest.source_text import snippet_contains_value, snippet_is_cached
from ..ledger import EvidenceLedger

CHECKS = {
    "seasonality": "Seasonality",
    "base_effect": "Base effects",
    "one_off_event": "One-off events",
    "accounting_change": "Accounting changes",
    "acquisition": "Acquisitions or demergers",
    "pricing_lag": "Pricing lags",
    "sector_trend": "Sector-wide movements",
}
OUTCOMES = {"supported", "disconfirmed", "unresolved"}


def benign_gap_share(*, explained_amount: float, gap_magnitude: float,
                     amount_unit: str | None, gap_unit: str | None) -> float | None:
    """Return an explained fraction only for valid, unit-matched inputs."""
    if not amount_unit or not gap_unit or amount_unit != gap_unit:
        return None
    try:
        explained_amount = float(explained_amount)
        gap_magnitude = abs(float(gap_magnitude))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(explained_amount) or not math.isfinite(gap_magnitude):
        return None
    if explained_amount < 0 or gap_magnitude <= 0 or explained_amount > gap_magnitude:
        return None
    return explained_amount / gap_magnitude


def _verified_sources(sources: object) -> list[dict]:
    if isinstance(sources, dict):
        sources = [sources]
    if not isinstance(sources, list):
        return []
    verified = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        path = source.get("cache_path")
        snippet = source.get("snippet")
        page = source.get("page")
        source_url = source.get("source_url")
        if (source.get("review_status") != "verified" or not source.get("reviewed_by")
                or not isinstance(source_url, str) or not source_url.startswith(("https://", "http://"))
                or not path or not isinstance(snippet, str) or not snippet or not Path(path).is_file()
                or (page is None and not source.get("locator"))
                or (Path(path).suffix.lower() == ".pdf" and (not isinstance(page, int) or page < 1))):
            continue
        try:
            digest = EvidenceLedger.sha256(path)
        except OSError:
            continue
        if digest != source.get("source_sha256") or not snippet_is_cached(path, snippet, page):
            continue
        verified.append({
            "source_url": source_url,
            "source_sha256": digest,
            "cache_path": str(path),
            "page": page,
            "locator": source.get("locator"),
            "snippet": snippet,
            "review_status": "verified",
            "reviewed_by": source["reviewed_by"],
        })
    return verified


def challenge(candidate: dict, evidence: dict | None = None) -> list[dict]:
    """Validate alternative-explanation evidence; absent/invalid evidence abstains.

    ``evidence`` is keyed by check ID. Each item may include an ``outcome`` and
    one or more reviewed cached ``sources``. ``benign_explained_amount`` is
    optional and is accepted only when a verified source snippet contains it.
    """
    evidence = evidence or {}
    gap = candidate.get("summary_numbers", {}).get("gap_magnitude")
    results = []
    for check_id, label in CHECKS.items():
        item = evidence.get(check_id, {})
        item = item if isinstance(item, dict) else {}
        sources = _verified_sources(item.get("sources"))
        outcome = item.get("outcome")
        valid_outcome = outcome in OUTCOMES
        if not sources or not valid_outcome:
            results.append({
                "test": check_id,
                "label": label,
                "outcome": "not_tested",
                "reason": "No reviewed source with a valid cached hash, locator, and exact snippet was supplied.",
                "sources": [],
                "benign_gap_share": None,
            })
            continue

        amount = item.get("benign_explained_amount")
        try:
            amount_supported = amount is not None and any(
                snippet_contains_value(source["snippet"], float(amount)) for source in sources
            )
        except (TypeError, ValueError):
            amount_supported = False
        share = benign_gap_share(explained_amount=amount, gap_magnitude=gap,
                                 amount_unit=item.get("amount_unit"),
                                 gap_unit=candidate.get("summary_numbers", {}).get("gap_unit")) if amount_supported else None
        results.append({
            "test": check_id,
            "label": label,
            "outcome": outcome,
            "reason": str(item.get("reason") or "Reviewed source evidence recorded."),
            "sources": sources,
            "benign_gap_share": share,
            "quantification_status": "source_supported" if share is not None else "not_quantified_or_unit_mismatch",
        })
    return results
