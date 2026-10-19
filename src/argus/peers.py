from .metrics import peer_adjusted_deviation

def period_key(row: dict) -> str:
    """Use an explicit period end for cross-company alignment when available."""
    return row.get("period_end") or row["period"]

def eligible_peer_panels(target: dict, panels: list[dict]) -> list[dict]:
    """Select panels with compatible basis, units, scope and overlapping periods.

    Cohort labels are local to each company (for example, a company's own demerger
    boundary) and therefore must not be compared by string equality across peers.
    Each company's panels are already split at its own cohort boundaries.
    """
    # A disclosed period-end date is a stronger cross-company key than labels such
    # as "FY26" versus "FY2025-26". Fall back to the source's exact label only
    # when the end date was not recorded.
    target_periods = {period_key(row) for row in target.get("periods", [])}
    result = []
    for panel in panels:
        if panel.get("company", "").casefold() == target.get("company", "").casefold():
            continue
        if panel.get("period_type") != target.get("period_type"):
            continue
        if panel.get("consolidation_basis") in (None, "unknown") or panel.get("consolidation_basis") != target.get("consolidation_basis"):
            continue
        if panel.get("currency") in (None, "unknown") or panel.get("currency") != target.get("currency"):
            continue
        target_scope = target.get("reporting_scope")
        peer_scope = panel.get("reporting_scope")
        if target_scope != peer_scope:
            continue
        peer_periods = {period_key(row) for row in panel.get("periods", [])}
        if target_periods and not target_periods.intersection(peer_periods):
            continue
        result.append(panel)
    return result

def compare_peer_gaps(company_gap: float, peer_gaps: list[float]) -> dict:
    deviation, status = peer_adjusted_deviation(company_gap, peer_gaps)
    return {"deviation": deviation, "status": status, "classification": "sector_story" if status == "tested" and deviation is not None and abs(deviation) < 1.5 else "company_specific" if status == "tested" else "insufficient"}
