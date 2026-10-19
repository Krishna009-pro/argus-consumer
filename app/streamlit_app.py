from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
import streamlit as st

st.set_page_config(page_title="ARGUS-Consumer", page_icon="◈", layout="wide")
st.markdown("<style>.block-container{max-width:1440px;padding-top:2rem}.hero{padding:1.4rem 1.7rem;border-radius:14px;background:linear-gradient(120deg,#10243a,#174c59);color:white}div[data-testid='stMetric']{background:#f4f7fa;padding:1rem;border-radius:10px}</style>", unsafe_allow_html=True)
st.markdown("<div class='hero'><h1>◈ ARGUS Consumer Intelligence</h1><p>Public evidence · deterministic metrics · explicit abstention</p></div>", unsafe_allow_html=True)
report_dir = ROOT / "reports"
reports = sorted(p for p in report_dir.glob("*.json")
                 if p.name.endswith(".json") and not p.name.endswith("-analysis.json")
                 and p.with_name(f"{p.stem}-analysis.json").is_file()) if report_dir.exists() else []
if not reports:
    st.info("No company dossiers are available. Run `make run COMPANY=...` after adding verified public data. No sample company data is shown.")
    st.stop()
selected = st.sidebar.selectbox("Company dossier", reports, format_func=lambda p: p.stem.replace("-", " ").title())
doc = json.loads(selected.read_text(encoding="utf-8"))
st.caption(f"Run state: {doc.get('validation', {}).get('state', 'unknown')} · All findings require verified public evidence.")
st.header(doc["discovery"])
left, right = st.columns([2,1])
with left:
    st.subheader("Why it matters")
    for item in doc["why_it_matters"]: st.write("• " + item)
    st.subheader("Timeline")
    if doc["timeline"]: st.dataframe(doc["timeline"], use_container_width=True)
    else: st.caption("No comparable validated periods are available.")
    st.subheader("Numerical evidence")
    if doc["numbers"]:
        for name, value in doc["numbers"].items(): st.write(f"**{name}**: {value}")
    else: st.caption("No verified numeric claims.")
with right:
    score_display = f"{doc['evidence_score']}/100" if doc.get("score_components") and doc.get("evidence") else None
    st.metric("Evidence strength", doc["evidence_label"], score_display)
    st.write("Score inputs", doc.get("score_components") or "Not scored: insufficient evidence.")
    st.subheader("Counterargument")
    st.write(doc["counterargument"])
    st.subheader("Falsification condition")
    st.write(doc["falsification_condition"])
st.subheader("Evidence trail")
ledger_path = ROOT / "data/ledger.jsonl"
ledger = [json.loads(x) for x in ledger_path.read_text(encoding="utf-8").splitlines() if x.strip()] if ledger_path.exists() else []
by_id = {entry["id"]: entry for entry in ledger}
if doc["evidence"]:
    for entry_id in doc["evidence"]:
        e = by_id.get(entry_id)
        if e:
            st.markdown(f"[{entry_id}: {e['source_type']} — {e['period']}]({e['source_url']})")
            st.caption(f"Page {e.get('doc_page') or 'not recorded'} · SHA-256 {e['source_sha256']} · {e['snippet']}")
else: st.caption("No source entries are linked yet.")
st.subheader("Not tested / abstentions")
for reason in doc["not_tested"]: st.write("• " + reason)
with st.expander("Unverified hypotheses and red-team checks"):
    st.warning("Hypotheses are not established facts.")
    st.write(doc.get("hypotheses") or "No AI research was performed.")
    st.write(doc.get("red_team_log") or "No evidence-backed red-team tests have been run.")
scoreboard = ROOT / "eval/results/scoreboard.md"
with st.expander("Evaluation scoreboard"):
    st.markdown(scoreboard.read_text(encoding="utf-8") if scoreboard.exists() else "No evaluation results have been generated.")
if st.button("Export dossier PDF"):
    try:
        from argus.schemas import Dossier
        from argus.report.pdf_export import build_pdf
        st.download_button("Download PDF", build_pdf(Dossier.model_validate(doc)), file_name=f"{selected.stem}.pdf", mime="application/pdf")
    except ImportError: st.error("PDF export needs the optional dashboard dependencies: pip install -e .[dashboard].")

# Panel inspection and method comparison are derived only from the saved run artifacts.
analysis_path = selected.with_name(f"{selected.stem}-analysis.json")
if analysis_path.is_file():
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    st.divider()
    st.header("Verified panels and comparison")
    st.caption("Panel values retain their reported periods, basis, scope, cohort and ledger IDs. Missing values remain blank.")
    try:
        import pandas as pd
    except ImportError:
        st.error("Panel inspection requires the optional dashboard dependencies: pip install -e .[dashboard].")
        pd = None
    if pd is not None:
        ledger_by_id = {entry.get("id"): entry for entry in ledger}
        for panel_number, result in enumerate(analysis.get("panels", []), start=1):
            panel = result["panel"]
            label = (f"{panel.get('consolidation_basis')} · {panel.get('reporting_scope')} · "
                     f"{panel.get('comparability_cohort')}")
            with st.expander(f"Panel {panel_number}: {label}", expanded=False):
                st.caption(f"{panel.get('period_type')} · {panel.get('currency')} · "
                           f"{', '.join(p['period'] for p in panel.get('periods', []))}")
                panel_rows = []
                for metric, values in panel.get("metrics", {}).items():
                    ids_by_period = panel.get("ledger_ids", {}).get(metric, [])
                    for i, period in enumerate(panel.get("periods", [])):
                        ids = ids_by_period[i] if i < len(ids_by_period) else []
                        panel_rows.append({"period": period.get("period"), "metric": metric,
                            "value": values[i] if i < len(values) else None,
                            "unit": panel.get("units", {}).get(metric), "ledger_ids": ", ".join(ids)})
                if panel_rows:
                    st.dataframe(pd.DataFrame(panel_rows), use_container_width=True, hide_index=True)
                    used_ids = list(dict.fromkeys(row["ledger_ids"] for row in panel_rows if row["ledger_ids"]))
                    for id_group in used_ids:
                        for entry_id in id_group.split(", "):
                            entry = ledger_by_id.get(entry_id)
                            if entry:
                                st.markdown(f"[{entry_id}: {entry.get('metric')} — {entry.get('period')}]({entry.get('source_url')})")
                                st.caption(f"PDF page {entry.get('doc_page')} · SHA-256 {entry.get('source_sha256')} · {entry.get('snippet')}")
                else:
                    st.info("This compatible panel has no verified metric values.")

                angle_rows = []
                for angle_name, angle in result.get("angles", {}).items():
                    for i, period in enumerate(angle.get("periods", [])):
                        reported = angle.get("reported", [None] * len(angle.get("periods", [])))[i]
                        if angle.get("status") == "tested" and reported is not None:
                            lows = angle.get("expected_low", [])
                            highs = angle.get("expected_high", [])
                            angle_rows.append({"period": period, "reported": reported,
                                "expected_low": lows[i] if i < len(lows) else None,
                                "expected_high": highs[i] if i < len(highs) else None})
                if angle_rows:
                    st.markdown("**Observed angle and historical expected range**")
                    chart_data = pd.DataFrame(angle_rows).dropna(subset=["reported"])
                    st.line_chart(chart_data.set_index("period"))
                else:
                    abstentions = [f"{name}: {value.get('abstain_reason', 'not tested')}"
                                   for name, value in result.get("angles", {}).items()
                                   if value.get("status") == "abstained"]
                    st.info("No tested angle series is available for this panel.")
                    for reason in abstentions:
                        st.write(f"• {reason}")

    st.subheader("Proof Panel")
    proof_left, proof_mid, proof_right = st.columns(3)
    validation = doc.get("validation", {})
    with proof_left:
        st.markdown("**ARGUS**")
        st.write(f"Run state: `{validation.get('state', 'unavailable')}`")
        st.write(f"Finding candidates: {len(validation.get('candidates', []))}")
        st.write(f"Rejected findings: {len(validation.get('rejected_findings', []))}")
    with proof_mid:
        st.markdown("**Ratio screen**")
        from eval.baselines.ratio_screen import flag as ratio_flag
        ratio_rows = []
        for result in analysis.get("panels", []):
            panel = result["panel"]
            values = panel.get("metrics", {}).get("revenue", [])
            periods = panel.get("periods", [])
            if len(values) >= 2 and len(periods) >= 2 and values[-2] not in (None, 0) and values[-1] is not None:
                change = values[-1] / values[-2] - 1
                ratio_rows.append({"basis": panel.get("consolidation_basis"), "period": periods[-1]["period"],
                    "revenue_change_pct": round(change * 100, 2), "screen_flag": ratio_flag(change)})
        if ratio_rows:
            st.dataframe(pd.DataFrame(ratio_rows), use_container_width=True, hide_index=True)
            st.caption("Existing ratio-screen rule: absolute annual change over 20%. This comparator is not ARGUS's finding gate.")
        else:
            st.caption("Unavailable: no verified comparable revenue periods.")
    with proof_right:
        st.markdown("**Plain LLM baseline**")
        st.caption("Unavailable: no blind baseline output or reviewer score is present. No summary was fabricated.")
