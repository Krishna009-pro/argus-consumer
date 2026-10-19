"""Build same-basis financial panels and derived metric series from verified ledger rows."""
from __future__ import annotations
from collections import defaultdict
from typing import Any
from .metrics import (price_mix_growth, receivable_days, inventory_days, cash_conversion,
                      margin_vs_input_cost, expected_range)
from .schemas import LedgerEntry

RAW_METRICS = {
    "revenue", "trade_receivables", "inventory", "cost_of_goods_sold", "operating_cash_flow",
    "ebitda", "volume_growth", "gross_margin", "input_cost_index",
}

def _period_order(entry: LedgerEntry) -> tuple[Any, ...]:
    if entry.period_end:
        return (0, entry.period_end.isoformat(), entry.period)
    return (1, entry.period.casefold())

def _period_days(entry: LedgerEntry) -> int | None:
    if entry.period_start and entry.period_end:
        return (entry.period_end - entry.period_start).days + 1
    return None

def build_company_panels(entries: list[LedgerEntry], company: str | None = None) -> list[dict]:
    """Duplicate metric-periods, mismatched units and conflicting basis stay unavailable."""
    verified = [e for e in entries if e.verified and e.company and e.cache_path]
    if company:
        verified = [e for e in verified if e.company.casefold() == company.casefold()]
    scopes: dict[tuple, list[LedgerEntry]] = defaultdict(list)
    for e in verified:
        if e.metric not in RAW_METRICS:
            continue
        scope = (e.company, e.period_type or "unknown", e.currency or "unknown", e.consolidation_basis,
                 e.reporting_scope or "unspecified", e.comparability_cohort or "unspecified")
        scopes[scope].append(e)
    panels = []
    for (name, period_type, currency, basis, reporting_scope, comparability_cohort), rows in scopes.items():
        periods = sorted({e.period for e in rows}, key=lambda p: min(_period_order(e) for e in rows if e.period == p))
        metrics: dict[str, list[float | None]] = {}
        ledger_ids: dict[str, list[list[str]]] = {}
        units_by_metric: dict[str, set[str]] = defaultdict(set)
        for row in rows: units_by_metric[row.metric].add(row.unit)
        unavailable: dict[str, str] = {}
        for metric in RAW_METRICS:
            if not any(r.metric == metric for r in rows):
                continue
            units = units_by_metric[metric]
            if len(units) != 1:
                unavailable[metric] = "Incompatible units across disclosed periods; no conversion was supplied."
                metrics[metric] = [None] * len(periods)
                ledger_ids[metric] = [[] for _ in periods]
                continue
            values, ids = [], []
            for period in periods:
                matches = [r for r in rows if r.metric == metric and r.period == period]
                if len(matches) > 1:
                    values.append(None); ids.append([])
                    unavailable[f"{metric}:{period}"] = "More than one verified value exists for this metric and period."
                elif matches:
                    values.append(matches[0].value); ids.append([matches[0].id])
                else:
                    values.append(None); ids.append([])
            metrics[metric], ledger_ids[metric] = values, ids
        period_rows = []
        for period in periods:
            period_entries = [e for e in rows if e.period == period]
            row = next((e for e in period_entries if e.period_start or e.period_end), period_entries[0])
            period_rows.append({"period": period, "period_type": period_type, "period_start": row.period_start.isoformat() if row.period_start else None,
              "period_end": row.period_end.isoformat() if row.period_end else None,
              "days": _period_days(row), "currency": currency, "consolidation_basis": basis,
              "reporting_scope": row.reporting_scope, "comparability_cohort": row.comparability_cohort})
        panels.append({"company": name, "period_type": period_type, "currency": currency, "consolidation_basis": basis,
                       "reporting_scope": reporting_scope, "comparability_cohort": comparability_cohort,
                       "periods": period_rows, "metrics": metrics, "ledger_ids": ledger_ids,
                       "units": {m: next(iter(us)) for m, us in units_by_metric.items() if len(us) == 1}, "unavailable": unavailable})
    return panels

def _growth(values: list[float | None]) -> list[float | None]:
    result: list[float | None] = [None]
    for previous, current in zip(values, values[1:]):
        result.append((current / previous - 1) if previous not in (None, 0) and current is not None else None)
    return result

def _combine_ids(*series: list[list[str]]) -> list[list[str]]:
    if not series: return []
    out = []
    for i in range(len(series[0])):
        out.append(list(dict.fromkeys(entry_id for group in series for entry_id in (group[i] if i < len(group) else []))))
    return out

def _growth_ids(ids: list[list[str]]) -> list[list[str]]:
    return [[]] + [list(dict.fromkeys(ids[i-1] + ids[i])) for i in range(1, len(ids))]

def derive_angle_series(panel: dict) -> dict[str, dict]:
    periods = panel["periods"]
    period_labels = [p["period"] for p in periods]
    raw = panel["metrics"]
    source_ids = panel["ledger_ids"]
    units = panel.get("units", {})
    out: dict[str, dict] = {}
    revenue = raw.get("revenue", [None] * len(periods))
    revenue_growth = _growth(revenue)
    volume = raw.get("volume_growth", [None] * len(periods))
    if units.get("volume_growth") in {"pct", "%", "percent"}:
        volume = [None if v is None else v / 100 for v in volume]
    price_mix = [price_mix_growth(rg, vg) for rg, vg in zip(revenue_growth, volume)]
    price_ids = _combine_ids(_growth_ids(source_ids.get("revenue", [[]] * len(periods))), source_ids.get("volume_growth", [[]] * len(periods)))
    out["price_volume"] = _angle("price_volume", period_labels, price_mix, price_ids)

    receivables = raw.get("trade_receivables", [None] * len(periods))
    compatible_rec_units = units.get("trade_receivables") == units.get("revenue") and units.get("revenue") is not None
    receivable_series = [receivable_days(v, rev, p.get("days") or 0) for v, rev, p in zip(receivables, revenue, periods)] if compatible_rec_units else [None] * len(periods)
    rec_ids = _combine_ids(source_ids.get("trade_receivables", [[]] * len(periods)), source_ids.get("revenue", [[]] * len(periods)))
    out["receivable_days"] = _angle("receivable_days", period_labels, receivable_series, rec_ids)

    inventory = raw.get("inventory", [None] * len(periods))
    cogs = raw.get("cost_of_goods_sold", [None] * len(periods))
    denominator_metric = "cost_of_goods_sold" if any(v is not None for v in cogs) else "revenue"
    denominator = cogs if denominator_metric == "cost_of_goods_sold" else revenue
    compatible_inventory_units = units.get("inventory") == units.get(denominator_metric) and units.get("inventory") is not None
    inventory_series = [inventory_days(inv, den, p.get("days") or 0) for inv, den, p in zip(inventory, denominator, periods)] if compatible_inventory_units else [None] * len(periods)
    inventory_ids = _combine_ids(source_ids.get("inventory", [[]] * len(periods)), source_ids.get(denominator_metric, [[]] * len(periods)))
    out["inventory_days"] = _angle("inventory_days", period_labels, inventory_series, inventory_ids,
      abstain_reason="Inventory, a same-unit positive denominator, and exact period day count are required.",
      metadata={"denominator": denominator_metric})

    ocf = raw.get("operating_cash_flow", [None] * len(periods))
    ebitda = raw.get("ebitda", [None] * len(periods))
    compatible_cash_units = units.get("operating_cash_flow") == units.get("ebitda") and units.get("ebitda") is not None
    cash_series = [cash_conversion(a, b) for a, b in zip(ocf, ebitda)] if compatible_cash_units else [None] * len(periods)
    cash_ids = _combine_ids(source_ids.get("operating_cash_flow", [[]] * len(periods)), source_ids.get("ebitda", [[]] * len(periods)))
    out["cash_conversion"] = _angle("cash_conversion", period_labels, cash_series, cash_ids)

    gross = raw.get("gross_margin", [None] * len(periods))
    gross_change = [None] + [(cur - prev) if cur is not None and prev is not None else None for prev, cur in zip(gross, gross[1:])]
    index = raw.get("input_cost_index", [None] * len(periods))
    index_change = _growth(index)
    margin_series = [margin_vs_input_cost(a, b * 100 if b is not None else None) for a, b in zip(gross_change, index_change)]
    margin_ids = _combine_ids(source_ids.get("gross_margin", [[]] * len(periods)), source_ids.get("input_cost_index", [[]] * len(periods)))
    out["margin_vs_input_cost"] = _angle("margin_vs_input_cost", period_labels, margin_series, margin_ids)
    for angle, result in out.items():
        if result["status"] == "abstained" and result["abstain_reason"] is None:
            result["abstain_reason"] = "Fewer than six usable disclosed periods for this angle."
    return out

def _angle(angle: str, periods: list[str], values: list[float | None], ids: list[list[str]], abstain_reason: str | None = None, metadata: dict | None = None) -> dict:
    available = sum(v is not None for v in values)
    if available < 6:
        return {"angle": angle, "status": "abstained", "abstain_reason": abstain_reason or "Fewer than six usable disclosed periods.",
                "periods": periods, "reported": values, "ledger_ids_by_period": ids, "metadata": metadata or {}}
    flags = [False] * len(values); lows = [None] * len(values); highs = [None] * len(values); spreads = [None] * len(values)
    for i in range(5, len(values)):
        historical = [v for v in values[:i + 1] if v is not None]
        bounds = expected_range(historical)
        if values[i] is not None and bounds:
            lows[i], highs[i], spreads[i] = bounds
            flags[i] = values[i] < lows[i] or values[i] > highs[i]
    return {"angle": angle, "status": "tested", "periods": periods, "reported": values, "expected_low": lows,
            "expected_high": highs, "expected_spread": spreads, "gap_flags": flags, "ledger_ids_by_period": ids, "metadata": metadata or {}}
