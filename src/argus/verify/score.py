from __future__ import annotations
from dataclasses import dataclass

@dataclass
class EvidenceScore:
    score: float
    label: str
    components: dict[str, float]

def calculate(persistence: int, gap: float, spread: float, peer_deviation: float,
              distinct_source_layers: int, robustness: float, insufficient_peers: bool = False) -> EvidenceScore:
    p = min(persistence / 6, 1)
    m = min(abs(gap) / (3 * spread), 1) if spread > 0 else (1.0 if gap != 0 else 0.0)
    peer = min(abs(peer_deviation) / 4, 1)
    sources = min(distinct_source_layers / 3, 1)
    robust = min(max(robustness, 0), 1)
    parts = {"persistence": 25*p, "magnitude": 20*m, "peer_adjusted": 20*peer, "independent_sources": 20*sources, "robustness": 15*robust}
    score = sum(parts.values())
    label = "Strong" if score >= 70 and distinct_source_layers >= 3 and persistence >= 4 else "Moderate" if score >= 45 and distinct_source_layers >= 2 else "Weak"
    if insufficient_peers: label = "Weak"
    return EvidenceScore(round(score, 2), label, parts)
