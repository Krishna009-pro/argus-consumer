"""Deterministic panel analysis, candidate gates, and provenance-preserving dossier payloads."""
from __future__ import annotations
from collections import defaultdict
from .metrics import longest_recent_run, peer_adjusted_deviation
from .panels import build_company_panels, derive_angle_series
from .schemas import Candidate, Dossier, LedgerEntry
from .validation_gate import validate
from .peers import eligible_peer_panels, period_key


def _peer_company_names(peer_panels: list[dict]) -> list[str]:
    """Return distinct peer entities when one peer has multiple compatible cohorts."""
    return list(dict.fromkeys(panel["company"] for panel in peer_panels))
from .verify.score import calculate as calculate_score
from .ledger import EvidenceLedger
from .agents.hypothesis import research
from .agents.redteam import challenge as challenge_red_team

ANGLE_SOURCE_METRICS = {
  "price_volume": {"revenue", "volume_growth"},
  "receivable_days": {"trade_receivables", "revenue"},
  "inventory_days": {"inventory", "cost_of_goods_sold", "revenue"},
  "cash_conversion": {"operating_cash_flow", "ebitda"},
  "margin_vs_input_cost": {"gross_margin", "input_cost_index"},
}

def _entry_layers(ids: list[str], by_id: dict[str, LedgerEntry]) -> int:
    types = {by_id[i].source_type for i in ids if i in by_id}
    urls = {by_id[i].source_url for i in ids if i in by_id}
    return max(len(types), len(urls), 1) if ids else 0

def _angle_residual(angle: dict, index: int) -> float | None:
    value = angle.get("reported", [])[index]
    low = angle.get("expected_low", [None] * (index+1))[index]
    high = angle.get("expected_high", [None] * (index+1))[index]
    if value is None or low is None or high is None: return None
    center = (low + high) / 2
    return abs(value - center)

def _angle_spread(angle: dict, index: int) -> float | None:
    values = angle.get("expected_spread", [])
    return values[index] if index < len(values) else None

def run_engine(entries: list[LedgerEntry], company: str) -> dict:
    """Run only on hash-verified, manually reviewed entries; return abstentions as data."""
    good = [e for e in entries if e.verified and e.verified_by and e.verified_at and e.company and e.cache_path
      and EvidenceLedger.sha256(e.cache_path) == e.source_sha256]
    by_id = {e.id: e for e in good}
    panels = build_company_panels(good)
    target_panels = [p for p in panels if p["company"].casefold() == company.casefold()]
    panel_analyses: list[dict] = []
    rejected: list[dict] = []
    for panel in target_panels:
        angles = derive_angle_series(panel)
        eligible_peers = eligible_peer_panels(panel, panels)
        windows_tested = sum(sum(v is not None for v in a.get("expected_low", [])) for a in angles.values())
        angle_evaluations = {}
        candidates = []
        for angle_name, angle in angles.items():
            angle_evaluations[angle_name] = angle
            persistence = longest_recent_run(angle.get("gap_flags", []))
            periods = angle.get("periods", [])
            if periods and angle.get("gap_flags") and angle["gap_flags"][-1] and persistence >= 1:
                latest = len(periods) - 1
                gap = _angle_residual(angle, latest)
                spread = _angle_spread(angle, latest)
                if gap is None or spread is None:
                    continue
                peer_gaps = []
                target_key = period_key(panel["periods"][latest])
                peer_panels_by_company: dict[str, list[dict]] = defaultdict(list)
                for peer_panel in eligible_peers:
                    peer_panels_by_company[peer_panel["company"].casefold()].append(peer_panel)
                for peer_panel_rows in peer_panels_by_company.values():
                    # Count a company once. If multiple panels from one company
                    # claim the same comparison period, treat that peer as ambiguous.
                    period_matches = [(peer_panel, [i for i, row in enumerate(peer_panel["periods"])
                        if period_key(row) == target_key]) for peer_panel in peer_panel_rows]
                    period_matches = [(peer_panel, indices) for peer_panel, indices in period_matches if indices]
                    if len(period_matches) != 1 or len(period_matches[0][1]) != 1:
                        continue
                    peer_panel, peer_indices = period_matches[0]
                    peer_angle = derive_angle_series(peer_panel).get(angle_name, {})
                    if peer_angle.get("status") != "tested":
                        continue
                    pi = peer_indices[0]
                    if pi is None or pi >= len(peer_angle.get("periods", [])):
                        continue
                    peer_gap = _angle_residual(peer_angle, pi)
                    if peer_gap is not None:
                        peer_gaps.append(peer_gap)
                peer_dev, peer_status = peer_adjusted_deviation(gap, peer_gaps)
                ids_by_period = angle.get("ledger_ids_by_period", [])
                ids = ids_by_period[latest] if latest < len(ids_by_period) else []
                hashes_valid = bool(ids) and all(i in by_id and by_id[i].cache_path and by_id[i].source_sha256 for i in ids)
                layers = _entry_layers(ids, by_id)
                gate = validate(persistence=persistence, peer_adjusted_deviation=peer_dev, hashes_valid=hashes_valid,
                  benign_gap_share=None, patterns_tested=max(windows_tested, 1), source_layers=layers)
                cand = Candidate(id=f"{company}:{panel['period_type']}:{periods[-1]}:{angle_name}", angles=[angle_name],
                  gap_start_period=periods[-persistence], summary_numbers={"gap_magnitude": gap, "spread": spread,
                    "persistence": float(persistence), "peer_gap_count": float(len(peer_gaps))}, gate=gate,
                  state="no_reliable_finding" if peer_status != "tested" or not gate["passed"] else "unexplained")
                candidates.append(cand.model_dump(mode="json"))
                # No external retrieval is configured. Record transparent query intent, but never
                # represent a planned query as a completed research or red-team test.
                research_result = research(cand.model_dump(mode="json"), offline=True)
                angle["research"] = {"status": research_result["status"], "queries": research_result["queries"]}
                # Without reviewed source evidence every alternative remains
                # not_tested; the red-team validator will not trust LLM claims.
                angle["red_team_tests"] = challenge_red_team(cand.model_dump(mode="json"))
                if not gate["passed"]:
                    rejected.append({"candidate_id": cand.id, "state": gate["state"], "gate": gate,
                                     "reason": "One or more evidence gates were not met; missing peer or red-team evidence is not treated as a pass."})
        panel_analyses.append({"panel": panel, "angles": angle_evaluations, "candidates": candidates,
                               "tested_patterns": windows_tested, "peer_companies": _peer_company_names(eligible_peers)})
    return {"company": company, "panels": panel_analyses, "rejected": rejected,
            "status": "analyzed" if panel_analyses else "abstained",
            "reason": None if panel_analyses else "No verified, compatible observations were available for this company."}

def make_dossier(analysis: dict, entries: list[LedgerEntry]) -> Dossier:
    company = analysis["company"]
    if not analysis["panels"]:
        return Dossier(company=company, discovery="No reliable finding: verified compatible financial observations are unavailable.",
          why_it_matters=["The analysis abstains rather than filling missing periods or metrics."], evidence=[], timeline=[], numbers={},
          counterargument="No company-specific finding was tested.", falsification_condition="Import and verify public observations from compatible filings, then rerun.",
          evidence_score=0, evidence_label="Weak", not_tested=[analysis["reason"] or "No compatible data."])
    rows = analysis["panels"]
    # Candidate state is dossier-wide: shorter later panels must not hide a valid
    # candidate generated from an earlier, compatible historical cohort.
    candidate_contexts = [(candidate, result) for result in rows for candidate in result["candidates"]]
    candidates = [candidate for candidate, _ in candidate_contexts]
    strong_contexts = [(candidate, result) for candidate, result in candidate_contexts
                       if candidate["state"] == "unexplained"]
    strong = [candidate for candidate, _ in strong_contexts]
    selected_result = strong_contexts[0][1] if strong_contexts else None
    primary_result = selected_result or max(rows, key=lambda result: result.get("tested_patterns", 0))
    panel = primary_result["panel"]
    angle_map = primary_result["angles"]
    evidence_ids = sorted({entry_id for result in rows for angle in result["angles"].values()
                           for period_ids in angle.get("ledger_ids_by_period", []) for entry_id in period_ids})
    by_id = {e.id: e for e in entries}
    numbers: dict[str, float] = {}
    timeline = []
    not_tested = []
    score = None
    for result in rows:
        result_panel = result["panel"]
        panel_label = ", ".join(str(result_panel.get(key) or "unspecified") for key in
                                 ("consolidation_basis", "reporting_scope", "comparability_cohort"))
        for angle_name, angle in result["angles"].items():
            if angle.get("status") != "tested":
                reason = angle.get("abstain_reason", "insufficient compatible disclosed inputs")
                not_tested.append(f"{panel_label} — {angle_name}: {reason}")
            for i, period in enumerate(angle.get("periods", [])):
                val = angle.get("reported", [None] * len(angle["periods"]))[i]
                low = angle.get("expected_low", [None] * len(angle["periods"]))[i]
                high = angle.get("expected_high", [None] * len(angle["periods"]))[i]
                ids_by_period = angle.get("ledger_ids_by_period", [])
                ids = ids_by_period[i] if i < len(ids_by_period) else []
                if val is not None and ids:
                    # Separate bracketed IDs satisfy the dossier's traceability
                    # contract even when several ledger rows support one value.
                    ledger_refs = " ".join(f"[{entry_id}]" for entry_id in ids)
                    numbers[f"{angle_name} {period} {ledger_refs}"] = val
                if i == len(angle["periods"]) - 1:
                    timeline.append({"period": period, "angle": angle_name, "reported": val, "expected_low": low,
                      "expected_high": high, "ledger_ids": ids, "status": angle.get("status", "abstained"),
                      "consolidation_basis": result_panel.get("consolidation_basis"),
                      "reporting_scope": result_panel.get("reporting_scope"),
                      "comparability_cohort": result_panel.get("comparability_cohort")})
    if strong:
        selected = strong[0]
        candidate_result = strong_contexts[0][1]
        angle_names = selected.get("angles", [])
        ids = []
        for angle_name in angle_names:
            angle = candidate_result["angles"].get(angle_name, {})
            if angle.get("periods"):
                ids.extend(angle.get("ledger_ids_by_period", [[]])[-1])
        ids = list(dict.fromkeys(i for i in ids if i in by_id))
        layers = _entry_layers(ids, by_id)
        score_result = calculate_score(persistence=int(selected["summary_numbers"].get("persistence", 0)), gap=selected["summary_numbers"].get("gap_magnitude", 0),
          spread=selected["summary_numbers"].get("spread", 0), peer_deviation=selected["gate"]["checks"]["peer_adjusted_deviation"]["observed"],
          distinct_source_layers=layers, robustness=1 - (selected["gate"]["checks"]["alternative_explanations"]["observed_benign_gap_share"] or 0.0),
          insufficient_peers=len(candidate_result["peer_companies"]) < 3)
        score = score_result
        discovery = f"A persistent historical-range deviation remains in {', '.join(selected['angles'])}; it is unverified as a business explanation."
    elif candidates:
        discovery = "A historical-range deviation was detected, but it did not clear peer and evidence validation; no finding is published."
    else:
        discovery = "No persistent, peer-adjusted anomaly cleared the deterministic screening criteria."
    peer_companies = list(dict.fromkeys(company for result in rows for company in result["peer_companies"]))
    if not peer_companies:
        not_tested.append("Peer-adjusted comparison: no eligible peer panels were available.")
    not_tested.extend([f"{x['candidate_id']}: {x['reason']}" for x in analysis["rejected"]])
    not_tested = list(dict.fromkeys(not_tested))
    return Dossier(company=company, discovery=discovery,
      why_it_matters=["Reported values are compared with the company’s own historical range.",
        "The workflow separates calculated deviations from explanations and abstains when independent evidence is missing."],
      evidence=evidence_ids, timeline=timeline, numbers=numbers,
      counterargument="Seasonality, base effects, one-off events, accounting changes, acquisitions, pricing lags and sector movement remain alternatives unless independently tested.",
      falsification_condition="The signal should be withdrawn if subsequent comparable periods return within the historical range or verified peer/source evidence explains the deviation.",
      evidence_score=score.score if score else 0, evidence_label=score.label if score else "Weak", not_tested=not_tested,
      red_team_log=[test for result in rows for angle in result["angles"].values()
                    for test in angle.get("red_team_tests", [])],
      score_components=score.components if score else {},
      validation={"state": "unexplained" if strong else "no_reliable_finding", "candidates": candidates,
        "rejected_findings": analysis["rejected"], "tested_patterns": sum(x["tested_patterns"] for x in rows),
        "panel_count": len(rows), "generated_candidates": [c for x in rows for c in x["candidates"]],
        "peer_companies": peer_companies, "period_type": panel["period_type"],
        "consolidation_basis": panel["consolidation_basis"], "reporting_scope": panel["reporting_scope"],
        "comparability_cohort": panel["comparability_cohort"]})
