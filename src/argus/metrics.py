from __future__ import annotations
from statistics import median
from .schemas import AngleResult

def price_mix_growth(revenue_growth: float | None, volume_growth: float | None) -> float | None:
    if revenue_growth is None or volume_growth is None or volume_growth <= -1:
        return None
    return (1 + revenue_growth) / (1 + volume_growth) - 1

def receivable_days(receivables: float | None, revenue: float | None, days: int) -> float | None:
    if receivables is None or revenue is None or revenue <= 0 or days <= 0: return None
    return receivables / revenue * days

def inventory_days(inventory: float | None, denominator: float | None, days: int) -> float | None:
    if inventory is None or denominator is None or denominator <= 0 or days <= 0: return None
    return inventory / denominator * days

def cash_conversion(operating_cash_flow: float | None, ebitda: float | None) -> float | None:
    if operating_cash_flow is None or ebitda is None or ebitda == 0: return None
    return operating_cash_flow / ebitda

def margin_vs_input_cost(gross_margin_change: float | None, input_index_change: float | None) -> float | None:
    if gross_margin_change is None or input_index_change is None: return None
    return gross_margin_change - input_index_change

def longest_recent_run(flags: list[bool]) -> int:
    run = 0
    for flag in reversed(flags):
        if not flag: break
        run += 1
    return run

def expected_range(values: list[float], minimum_history: int = 6) -> tuple[float, float, float] | None:
    """Plan: center/spread from history excluding latest two observations."""
    if len(values) < minimum_history:
        return None
    history = values[:-2]
    if not history: return None
    center = median(history)
    mad = median([abs(value - center) for value in history])
    spread = 1.4826 * mad
    return center - 2 * spread, center + 2 * spread, spread

def peer_adjusted_deviation(company_gap: float, peer_gaps: list[float]) -> tuple[float | None, str]:
    if len(peer_gaps) < 3: return None, "insufficient"
    center = median(peer_gaps)
    mad = median([abs(v - center) for v in peer_gaps])
    if mad == 0:
        return None, "zero_dispersion"
    return (company_gap - center) / mad, "tested"

def angle_result(angle: str, periods: list[str], values: list[float | None], ledger_ids: list[str]) -> AngleResult:
    valid = [v for v in values if v is not None]
    if len(valid) < 6:
        return AngleResult(angle=angle, status="abstained", abstain_reason="Fewer than six disclosed periods.", periods=periods, ledger_ids=ledger_ids)
    flags = [False] * len(values)
    lows: list[float | None] = [None] * len(values)
    highs: list[float | None] = [None] * len(values)
    for index in range(5, len(values)):
        history = [v for v in values[:index + 1] if v is not None]
        bounds = expected_range(history)
        if values[index] is not None and bounds:
            low, high, _ = bounds
            lows[index], highs[index] = low, high
            flags[index] = values[index] < low or values[index] > high
    return AngleResult(angle=angle, status="tested", series={"reported": values, "expected_low": lows, "expected_high": highs}, periods=periods, gap_flags=flags, persistence_periods=longest_recent_run(flags), ledger_ids=ledger_ids)
