from .metrics import expected_range, longest_recent_run, peer_adjusted_deviation

def build_range(values: list[float], minimum_history: int = 6):
    return expected_range(values, minimum_history)

__all__ = ["build_range", "longest_recent_run", "peer_adjusted_deviation"]
