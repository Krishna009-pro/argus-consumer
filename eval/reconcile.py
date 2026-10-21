"""Compare deterministic metrics with verified, formula-compatible published figures."""
from __future__ import annotations

import json
from pathlib import Path

from argus.ledger import EvidenceLedger
from argus.metrics import (cash_conversion, inventory_days, margin_vs_input_cost,
                           price_mix_growth, receivable_days)


DATA_PATH = Path("data/reconciliation/published_figures.json")
FORMULAS = {
    "price_volume": "price_mix_from_revenue_growth_and_volume_growth",
    "receivable_days": "closing_trade_receivables_over_revenue_from_operations_times_period_days",
    "inventory_days": {
        "revenue": "closing_inventory_over_revenue_from_operations_times_period_days",
        "cost_of_goods_sold": "closing_inventory_over_cost_of_goods_sold_times_period_days",
    },
    "cash_conversion": "operating_cash_flow_over_ebitda",
    "margin_vs_input_cost": "gross_margin_change_minus_input_cost_index_growth_percentage_points",
}


def _engine_value(reference: dict, entries: list) -> float | None:
    """Recompute a supported ARGUS formula from exact company-period ledger rows."""
    def period_entries(period: str) -> list:
        return [e for e in entries if e.company == reference.get("company") and e.period == period
                and e.consolidation_basis == reference.get("basis")
                and e.reporting_scope == reference.get("reporting_scope")
                and e.comparability_cohort == reference.get("comparability_cohort") and e.verified]

    def values_for(period: str) -> tuple[dict[str, float], dict[str, str]] | None:
        values: dict[str, float] = {}
        units: dict[str, str] = {}
        for entry in period_entries(period):
            if entry.metric in {"revenue", "trade_receivables", "inventory", "cost_of_goods_sold",
                                "volume_growth", "operating_cash_flow", "ebitda", "gross_margin",
                                "input_cost_index"}:
                if entry.metric in values:
                    return None
                values[entry.metric] = entry.value
                units[entry.metric] = entry.unit
        return values, units

    current = values_for(reference.get("period", ""))
    if current is None:
        return None
    values, units = current
    metric = reference.get("engine_metric")
    if metric == "price_volume":
        prior_period = reference.get("prior_period")
        prior = values_for(prior_period) if prior_period else None
        if prior is None or not {"revenue", "volume_growth"} <= values.keys() or "revenue" not in prior[0]:
            return None
        prior_values, prior_units = prior
        if prior_values["revenue"] == 0 or units.get("revenue") != prior_units.get("revenue") or units.get("revenue") != "INR_crore":
            return None
        volume = values["volume_growth"]
        if units.get("volume_growth", "").casefold() in {"pct", "%", "percent"}:
            volume /= 100
        return price_mix_growth(values["revenue"] / prior_values["revenue"] - 1, volume)
    if metric == "cash_conversion" and {"operating_cash_flow", "ebitda"} <= values.keys():
        if units.get("operating_cash_flow") != units.get("ebitda"):
            return None
        return cash_conversion(values["operating_cash_flow"], values["ebitda"])
    if metric == "margin_vs_input_cost":
        prior_period = reference.get("prior_period")
        prior = values_for(prior_period) if prior_period else None
        if prior is None or not {"gross_margin", "input_cost_index"} <= values.keys():
            return None
        prior_values, prior_units = prior
        if not {"gross_margin", "input_cost_index"} <= prior_values.keys():
            return None
        if units.get("gross_margin") != prior_units.get("gross_margin") or units.get("input_cost_index") != prior_units.get("input_cost_index"):
            return None
        if prior_values["input_cost_index"] == 0:
            return None
        index_growth = values["input_cost_index"] / prior_values["input_cost_index"] - 1
        return margin_vs_input_cost(values["gross_margin"] - prior_values["gross_margin"], index_growth * 100)
    period_rows = [e for e in period_entries(reference.get("period", "")) if e.period_start and e.period_end]
    if not period_rows:
        return None
    from datetime import date
    start = date.fromisoformat(period_rows[0].period_start)
    end = date.fromisoformat(period_rows[0].period_end)
    days = (end - start).days + 1
    if metric == "receivable_days" and {"trade_receivables", "revenue"} <= values.keys():
        if units.get("trade_receivables") != units.get("revenue") or units.get("revenue") != "INR_crore":
            return None
        return receivable_days(values["trade_receivables"], values["revenue"], days)
    if metric == "inventory_days":
        denominator_metric = reference.get("denominator_metric", "revenue")
        denominator = values.get(denominator_metric)
        if denominator is None or "inventory" not in values:
            return None
        if units.get("inventory") != units.get(denominator_metric):
            return None
        return inventory_days(values["inventory"], denominator, days)
    return None


def evaluate(path: str | Path = DATA_PATH) -> dict:
    """Return M01 plus explicit exclusions; unmatched formulas never enter the denominator."""
    source_path = Path(path)
    if not source_path.exists():
        return {"metric": "M01_reconciliation_rate", "value": None, "matched": 0,
                "compared": 0, "excluded": 0, "status": "unavailable_no_published_figure_dataset",
                "exclusions": []}
    dataset = json.loads(source_path.read_text(encoding="utf-8"))
    references = dataset.get("references", [])
    ledger = EvidenceLedger()
    entries = None
    readers = {}
    source_hashes = {}
    matches: list[dict] = []
    exclusions: list[dict] = []
    for reference in references:
        reason = None
        cache = Path(reference.get("cache_path", ""))
        cache_key = str(cache)
        if reference.get("review_status") != "verified" or not reference.get("verified_by"):
            reason = "published reference has not been manually verified"
        elif not cache.is_file():
            reason = "cached source is missing or its SHA-256 does not match"
        else:
            if cache_key not in source_hashes:
                source_hashes[cache_key] = EvidenceLedger.sha256(cache)
            if source_hashes[cache_key] != reference.get("source_sha256"):
                reason = "cached source is missing or its SHA-256 does not match"
            else:
                if cache_key not in readers:
                    readers[cache_key] = _open_reader(cache)
                if not _source_snippets_match(reference, readers[cache_key]):
                    reason = "published value or formula snippet is not present on its cited cached PDF page"
        expected_formula = FORMULAS.get(reference.get("engine_metric"))
        if isinstance(expected_formula, dict):
            expected_formula = expected_formula.get(reference.get("denominator_metric", "revenue"))
        if reason is None and reference.get("engine_formula_id") != expected_formula:
            reason = "engine formula identifier is unsupported"
        elif reason is None and reference.get("published_formula_id") != reference.get("engine_formula_id"):
            reason = "published and ARGUS formulas differ"
        if reason:
            exclusions.append({"company": reference.get("company"), "period": reference.get("period"),
                               "published_metric": reference.get("published_metric"), "reason": reason,
                               "source_url": reference.get("source_url"), "page": reference.get("page")})
            continue
        if entries is None:
            entries = ledger.verified_entries()
        calculated = _engine_value(reference, entries)
        if calculated is None:
            exclusions.append({"company": reference["company"], "period": reference["period"],
                               "published_metric": reference["published_metric"],
                               "reason": "verified matching ledger inputs or exact period dates are unavailable",
                               "source_url": reference["source_url"], "page": reference["page"]})
            continue
        reported = float(reference["published_value"])
        tolerance = max(abs(reported) * 0.005, float(reference["rounding_unit"]))
        error = abs(calculated - reported)
        matches.append({"company": reference["company"], "period": reference["period"],
                        "published_metric": reference["published_metric"], "calculated": calculated,
                        "published": reported, "absolute_error": error, "tolerance": tolerance,
                        "matched": error <= tolerance, "source_url": reference["source_url"],
                        "page": reference["page"]})
    compared = len(matches)
    matched = sum(bool(item["matched"]) for item in matches)
    return {"metric": "M01_reconciliation_rate", "value": matched / compared if compared else None,
            "matched": matched, "compared": compared, "excluded": len(exclusions),
            "status": "measured" if compared else "unavailable_no_comparable_published_figures",
            "matches": matches, "exclusions": exclusions}


def _open_reader(cache: Path):
    from pypdf import PdfReader
    return PdfReader(str(cache))


def _source_snippets_match(reference: dict, reader) -> bool:
    try:
        value_page = reader.pages[int(reference["page"]) - 1].extract_text() or ""
        formula_page = reader.pages[int(reference["formula_page"]) - 1].extract_text() or ""
    except (IndexError, KeyError, TypeError, ValueError):
        return False
    normalize = lambda text: " ".join(text.split())
    return bool(reference.get("page") and reference.get("formula_page")
                and normalize(reference.get("snippet", "")) in normalize(value_page)
                and normalize(reference.get("formula_snippet", "")) in normalize(formula_page))
