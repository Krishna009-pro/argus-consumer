def flag(year_on_year_change: float | None, threshold: float = 0.2) -> bool | None:
    if year_on_year_change is None: return None
    return abs(year_on_year_change) > threshold
