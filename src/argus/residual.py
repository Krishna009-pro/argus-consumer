from .metrics import expected_range

def detect(values: list[float], minimum_history: int = 6) -> dict:
    flags = [False] * len(values)
    lows: list[float | None] = [None] * len(values)
    highs: list[float | None] = [None] * len(values)
    for i in range(len(values)):
        bounds = expected_range(values[:i + 1], minimum_history)
        if bounds:
            lows[i], highs[i], _ = bounds
            flags[i] = values[i] < bounds[0] or values[i] > bounds[1]
    return {"flags": flags, "low": lows, "high": highs}
