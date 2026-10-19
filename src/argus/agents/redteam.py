CHECKS = ("seasonality", "base effects", "one-off events", "accounting changes", "acquisitions or demergers", "pricing lags", "sector-wide movements")

def challenge(candidate: dict, evidence: dict | None = None) -> list[dict]:
    evidence = evidence or {}
    return [{"test": item, "outcome": "not_tested" if item not in evidence else str(evidence[item].get("outcome", "unresolved")),
             "reason": "No verified source evidence was supplied for this alternative." if item not in evidence else str(evidence[item].get("reason", "Recorded from supplied evidence.")),
             "benign_gap_share": evidence.get(item, {}).get("benign_gap_share")}
            for item in CHECKS]
