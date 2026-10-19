from pathlib import Path
from argus.ledger import EvidenceLedger

def evaluate() -> dict:
    ledger = EvidenceLedger()
    entries = ledger.entries()
    valid = sum(ledger.verify(e) for e in entries)
    invalid = len(entries) - valid
    return {"M02_claim_grounding_rate": 100 * valid / len(entries) if entries else None,
            "M03_unsupported_claims": 0 if not entries else invalid, "checked": len(entries), "valid": valid,
            "status": "no_claims_to_check" if not entries else "measured"}
