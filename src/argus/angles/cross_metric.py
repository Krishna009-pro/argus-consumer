def combine(angle_flags: dict[str, list[bool]], periods: list[str]) -> list[dict]:
    found = []
    for i, period in enumerate(periods):
        flagged = [name for name, flags in angle_flags.items() if i < len(flags) and flags[i]]
        if len(flagged) >= 2:
            found.append({"period": period, "angles": flagged, "sequence_first": flagged[0], "causal_claim": False})
    return found
