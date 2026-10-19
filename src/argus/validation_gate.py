from __future__ import annotations
from math import log2

def validate(*, persistence: int, peer_adjusted_deviation: float | None, hashes_valid: bool,
             benign_gap_share: float | None, patterns_tested: int, source_layers: int) -> dict:
    threshold = 1.5 + 0.25 * log2(max(patterns_tested, 1))
    checks = {
      "persistence": {"passed": persistence >= 3, "observed": persistence, "required": 3},
      "peer_adjusted_deviation": {"passed": peer_adjusted_deviation is not None and peer_adjusted_deviation >= 1.5, "observed": peer_adjusted_deviation, "required": 1.5},
      "data_quality": {"passed": hashes_valid, "observed": hashes_valid},
      "alternative_explanations": {"passed": benign_gap_share is not None and benign_gap_share <= 0.60, "observed_benign_gap_share": benign_gap_share, "required_max": 0.60},
      "multiple_testing": {"passed": peer_adjusted_deviation is not None and peer_adjusted_deviation >= threshold, "observed": peer_adjusted_deviation, "required": threshold, "patterns_tested": patterns_tested},
      "independent_source_layers": {"passed": source_layers >= 2, "observed": source_layers, "required": 2},
    }
    passed = all(item["passed"] for item in checks.values())
    return {"checks": checks, "passed": passed, "state": "unexplained" if passed else "rejected", "label_cap": "Weak" if source_layers < 3 or (peer_adjusted_deviation is not None and peer_adjusted_deviation < threshold) else None}
