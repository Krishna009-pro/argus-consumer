from __future__ import annotations
from ..schemas import Dossier

def abstention_dossier(company: str, reasons: list[str] | None = None) -> Dossier:
    reasons = reasons or ["No verified public financial inputs are present in the local cache."]
    return Dossier(company=company, discovery="No reliable finding: required source data are unavailable.",
      why_it_matters=["The system abstains when evidence is insufficient."], evidence=[], timeline=[], numbers={},
      counterargument="No finding is asserted; disclosed data may be available outside the local cache.",
      falsification_condition="Re-run after adding verified public filings and comparable period inputs.",
      evidence_score=0, evidence_label="Weak", not_tested=reasons)

def render(dossier: Dossier) -> str:
    lines = [f"# ARGUS-Consumer dossier — {dossier.company}", "", "## Discovery", dossier.discovery,
      "", "## Why it matters"]
    lines.extend(f"- {item}" for item in dossier.why_it_matters)
    lines += ["", "## Linked evidence"] + ([f"- {item}" for item in dossier.evidence] or ["- No verified ledger evidence available."])
    lines += ["", "## Timeline"] + ([f"- {item}" for item in dossier.timeline] or ["- Not available."])
    lines += ["", "## Numerical evidence"] + ([f"- {key}: {value}" for key, value in dossier.numbers.items()] or ["- No verified numeric claims."])
    lines += ["", "## Counterargument", dossier.counterargument, "", "## Falsification condition", dossier.falsification_condition,
      "", "## Evidence strength", f"{dossier.evidence_label} (score {dossier.evidence_score})" if dossier.evidence else f"{dossier.evidence_label} (score not calculated: verified evidence unavailable)", "", "## Not tested"]
    lines.extend(f"- {item}" for item in dossier.not_tested)
    lines += ["", "## Hypotheses (unverified)"] + ([f"- {h}" for h in dossier.hypotheses] or ["- None; optional research model is not configured or no source excerpts were available."])
    lines += ["", "## Red-team review"] + ([f"- {x.get('test')}: {x.get('outcome')} — {x.get('reason')}" for x in dossier.red_team_log] or ["- Not run."])
    return "\n".join(lines) + "\n"
