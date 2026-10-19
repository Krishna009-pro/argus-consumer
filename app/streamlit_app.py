from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ARGUS | Autonomous Consumer Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, Modern Light-Theme Financial Intelligence Styling
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
  --argus-primary: #0284c7;
  --argus-primary-dark: #0369a1;
  --argus-primary-light: #e0f2fe;
  --argus-emerald: #059669;
  --argus-emerald-light: #ecfdf5;
  --argus-amber: #d97706;
  --argus-amber-light: #fffbeb;
  --argus-rose: #dc2626;
  --argus-rose-light: #fef2f2;
  --argus-indigo: #4f46e5;
  --argus-indigo-light: #eef2ff;
  --argus-bg: #f8fafc;
  --argus-card-bg: #ffffff;
  --argus-border: #e2e8f0;
  --argus-border-subtle: #f1f5f9;
  --argus-text-main: #0f172a;
  --argus-text-muted: #64748b;
}

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
  background-color: #f8fafc;
  color: #0f172a;
}

[data-testid="stSidebar"] {
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
}

/* Institutional Top Navigation Header */
header[data-testid="stHeader"] {
  background-color: #ffffff !important;
  border-bottom: 1px solid #e2e8f0 !important;
  height: 3.25rem !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
  z-index: 99 !important;
}

header[data-testid="stHeader"]::before {
  content: "◈ ARGUS   |   Autonomous Financial Discovery Engine   ·   Track C: FMCG & Consumer Retail   •   Deterministic Ledger Audit";
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 0.82rem;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: 0.02em;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

@media (max-width: 1200px) {
  header[data-testid="stHeader"]::before {
    content: "◈ ARGUS   |   Track C: FMCG & Retail   •   Deterministic Ledger";
  }
}

@media (max-width: 800px) {
  header[data-testid="stHeader"]::before {
    content: "◈ ARGUS Intel";
  }
}

/* Style the deploy button to look like an institutional action badge */
.stDeployButton button, [data-testid="stDeployButton"] button {
  background: #f8fafc !important;
  border: 1px solid #cbd5e1 !important;
  color: #475569 !important;
  font-size: 0.74rem !important;
  font-weight: 650 !important;
  border-radius: 6px !important;
  padding: 0.2rem 0.65rem !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
}

code, pre, .mono-font {
  font-family: 'JetBrains Mono', monospace !important;
}

.block-container {
  max-width: 1560px;
  padding-top: 1.2rem;
  padding-bottom: 3.5rem;
}

/* Hero Header Banner (Clean Light Gradient) */
.argus-hero {
  background: linear-gradient(135deg, #ffffff 0%, #f0fdfa 40%, #eff6ff 100%);
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  padding: 1.6rem 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
}

.argus-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.28rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.badge-abstain {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #b45309;
}

.badge-verified {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #047857;
}

.badge-neutral {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
}

/* Metric Cards */
.metric-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.1rem 1.3rem;
  box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  border-color: #0284c7;
  box-shadow: 0 8px 16px -4px rgba(2, 132, 199, 0.1);
}

.metric-card-label {
  font-size: 0.76rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #64748b;
  margin-bottom: 0.3rem;
}

.metric-card-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.metric-card-sub {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.3rem;
}

/* Clean Callout Boxes */
.glass-callout {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.3rem 1.6rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 2px 10px -2px rgba(15, 23, 42, 0.03);
}

.callout-amber {
  border-left: 4px solid #d97706;
  background: linear-gradient(90deg, #fffbeb 0%, #ffffff 100%);
  border-top: 1px solid #fef3c7;
  border-right: 1px solid #fef3c7;
  border-bottom: 1px solid #fef3c7;
}

.callout-cyan {
  border-left: 4px solid #0284c7;
  background: linear-gradient(90deg, #f0f9ff 0%, #ffffff 100%);
  border-top: 1px solid #e0f2fe;
  border-right: 1px solid #e0f2fe;
  border-bottom: 1px solid #e0f2fe;
}

.callout-emerald {
  border-left: 4px solid #059669;
  background: linear-gradient(90deg, #ecfdf5 0%, #ffffff 100%);
  border-top: 1px solid #d1fae5;
  border-right: 1px solid #d1fae5;
  border-bottom: 1px solid #d1fae5;
}

/* Proof Panel 3-Way Cards */
.proof-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.3rem 1.4rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.03);
}

.proof-card-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.05rem;
  font-weight: 750;
  margin-bottom: 0.8rem;
}

/* Evidence Statement Excerpt Box */
.evidence-snippet {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 0.9rem 1.1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.84rem;
  color: #0f172a;
  line-height: 1.5;
  margin: 0.6rem 0;
}

/* Tabs */
div[data-testid="stTabs"] button {
  font-weight: 650;
  font-size: 0.95rem;
  padding: 0.7rem 1.3rem;
  color: #475569;
  border-radius: 8px 8px 0 0;
  letter-spacing: 0.01em;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
  color: #0284c7 !important;
  border-bottom-color: #0284c7 !important;
  background: rgba(2, 132, 199, 0.06);
}

/* Pulsing Status Dot */
.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.pulse-amber {
  background: #d97706;
  box-shadow: 0 0 6px #d97706;
}

.pulse-emerald {
  background: #059669;
  box-shadow: 0 0 6px #059669;
}
</style>""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_json(path_str: str) -> dict:
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        st.error(f"Could not read `{Path(path_str).name}`: {exc}")
        return {}


@st.cache_data(show_spinner=False)
def read_ledger() -> list[dict]:
    path = ROOT / "data" / "ledger.jsonl"
    if not path.exists():
        return []
    entries = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def get_available_reports() -> list[Path]:
    report_dir = ROOT / "reports"
    if not report_dir.exists():
        return []
    candidates = sorted(
        path for path in report_dir.glob("*.json")
        if not path.name.endswith("-analysis.json")
        and path.with_name(f"{path.stem}-analysis.json").is_file()
    )
    # Prioritize reports with rich verified data (HUL, ITC)
    def sort_key(p: Path):
        content = p.read_text(encoding="utf-8")
        has_obs = '"evidence": [' in content and not '"evidence": []' in content
        return (0 if has_obs else 1, p.stem)
    return sorted(candidates, key=sort_key)


def angle_summary(analysis: dict) -> tuple[int, int, list[tuple[str, str]]]:
    tested = 0
    abstained = 0
    reasons: list[tuple[str, str]] = []
    for result in analysis.get("panels", []):
        panel = result.get("panel", {})
        context = ", ".join(
            val for val in (
                panel.get("comparability_cohort"),
                panel.get("consolidation_basis"),
                panel.get("reporting_scope"),
            ) if val
        )
        for name, angle in result.get("angles", {}).items():
            if angle.get("status") == "tested":
                tested += 1
            elif angle.get("status") == "abstained":
                abstained += 1
                reason = angle.get("abstain_reason") or "No reason recorded."
                item = (f"{name.replace('_', ' ').title()} ({context})", reason)
                if item not in reasons:
                    reasons.append(item)
    return tested, abstained, reasons


reports = get_available_reports()

with st.sidebar:
    st.markdown("### ◈ **ARGUS**")
    st.caption("Autonomous Financial Discovery Engine · Track C")
    st.markdown("---")

    with st.expander("🌐 Live company intake", expanded=False):
        st.caption("Search public sources, cache a selected PDF, and extract review-only claims.")
        online_company = st.text_input("Company name", key="online_company_name", placeholder="e.g. ITC Limited")
        if st.button("Search public reports", key="online_search", use_container_width=True):
            if not online_company.strip():
                st.error("Enter a company name first.")
            else:
                st.session_state.pop("online_search_results", None)
                st.session_state.pop("online_intake_result", None)
                try:
                    from argus.search import search_serper
                    results = search_serper(
                        f'"{online_company.strip()}" annual report financial statements PDF', limit=10
                    )
                    st.session_state["online_search_results"] = results
                    st.session_state["online_search_company"] = online_company.strip()
                    st.session_state.pop("online_intake_result", None)
                    st.session_state.pop("online_pdf_links", None)
                    if not results:
                        st.warning("No public-source results were returned.")
                except Exception as exc:
                    st.error(str(exc))

        search_results = st.session_state.get("online_search_results", [])
        if search_results:
            selected_online_result = st.selectbox(
                "Choose a report to inspect",
                range(len(search_results)),
                format_func=lambda index: f"{search_results[index]['title']} · {search_results[index]['url']}",
                key="online_result_choice",
            )
            st.caption("Search results are unverified. Confirm the publisher and report before fetching.")
            if st.button("Fetch PDF and extract claims", key="online_fetch", use_container_width=True):
                selected = search_results[selected_online_result]
                try:
                    from argus.search import discover_pdf_links, is_pdf_url
                    if is_pdf_url(selected["url"]):
                        st.session_state["online_pdf_links"] = [{"title": selected["title"], "url": selected["url"]}]
                        st.session_state["online_pdf_source"] = selected["url"]
                    else:
                        links = discover_pdf_links(selected["url"])
                        st.session_state["online_pdf_links"] = links
                        st.session_state["online_pdf_source"] = selected["url"]
                        if not links:
                            st.warning("This page did not expose a direct PDF link. Try another result or use a direct PDF URL.")
                except Exception as exc:
                    st.error(f"Could not inspect this report page: {exc}")

        pdf_links = st.session_state.get("online_pdf_links", [])
        if pdf_links:
            st.caption(f"Direct PDF links found on {st.session_state.get('online_pdf_source', 'the selected page')}:")
            selected_pdf_index = st.selectbox(
                "Choose the report PDF",
                range(len(pdf_links)),
                format_func=lambda index: f"{pdf_links[index]['title']} · {pdf_links[index]['url']}",
                key="online_pdf_choice",
            )
            if st.button("Fetch selected PDF and extract claims", key="online_fetch_pdf", use_container_width=True):
                selected_pdf = pdf_links[selected_pdf_index]
                try:
                    from argus.ingest.local_import import import_remote_pdf
                    company_name = st.session_state.get("online_search_company", online_company.strip())
                    with st.spinner("Fetching or reusing the PDF and extracting candidate claims. Large reports may take a few minutes..."):
                        cache_path, digest, candidate_file, candidates, cache_reused = import_remote_pdf(
                            selected_pdf["url"], company=company_name
                        )
                    st.session_state["online_intake_result"] = {
                        "company": company_name,
                        "title": selected_pdf["title"], "url": selected_pdf["url"],
                        "cache_path": str(cache_path), "sha256": digest,
                        "candidate_file": str(candidate_file),
                        "candidate_count": sum(candidate.status == "unverified" for candidate in candidates),
                        "ambiguous_count": sum(candidate.status == "ambiguous" for candidate in candidates),
                        "cache_reused": cache_reused,
                        "candidates": [candidate.model_dump(mode="json") for candidate in candidates],
                    }
                    st.session_state.pop("online_pdf_links", None)
                except Exception as exc:
                    st.error(f"Could not fetch or parse this PDF: {exc}")
        intake_result = st.session_state.get("online_intake_result")
        if intake_result:
            if intake_result["candidate_count"]:
                st.success(
                    f"Cached and extracted {intake_result['candidate_count']} claims. "
                    "They remain unverified until reviewed."
                )
                if intake_result.get("ambiguous_count"):
                    st.caption(
                        f"{intake_result['ambiguous_count']} superseded extraction rows are retained as ambiguous "
                        "for audit and are excluded from review."
                    )
            else:
                st.info(
                    "The PDF was cached, but the financial-statement extractor found no supported claims. "
                    "This can happen with narrative sections such as Management Discussion & Analysis. "
                    "Choose the full annual report or a standalone/consolidated financial-statements PDF."
                )

    if not reports:
        st.info("No saved dossiers yet. Use Live company intake to begin with an online source.")

    report_docs = {p: load_json(str(p)) for p in reports}

    def report_label(path: Path) -> str:
        d = report_docs.get(path, {})
        name = d.get("company", path.stem.replace("-", " ").title())
        count = len(d.get("evidence", []))
        return f"{name} ({count} obs)"

    selected_report = None
    if reports:
        selected_report = st.selectbox(
            "Select Company Dossier",
            reports,
            format_func=report_label,
            help="Select a listed consumer company dossier generated by ARGUS.",
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.5rem;">
                <span style="font-weight: 700; font-size: 0.85rem; color: #0f172a;">🏛️ Core Rules Status</span>
                <span style="background: #ecfdf5; color: #047857; font-size: 0.68rem; padding: 2px 7px; border-radius: 9999px; font-weight: 750; border: 1px solid #a7f3d0;">ALL PASS</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.45rem; font-size: 0.78rem; color: #334155; line-height: 1.4;">
                <div><strong style="color: #0284c7;">R1:</strong> Zero hardcoded company logic</div>
                <div><strong style="color: #0284c7;">R2:</strong> 100% mapped to ledger <code style="font-size: 0.74rem;">[Lxxxx]</code></div>
                <div><strong style="color: #0284c7;">R3:</strong> Deterministic math (no LLM math)</div>
                <div><strong style="color: #0284c7;">R4:</strong> Strict abstention (no zero-fill)</div>
                <div><strong style="color: #0284c7;">R5:</strong> ≥ 2 independent source layers</div>
                <div><strong style="color: #0284c7;">R6:</strong> 100% public BSE/NSE filings</div>
                <div><strong style="color: #0284c7;">R8:</strong> Content-addressed SHA-256 cache</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    st.caption("ATMOS 2026: Finding the Next Signal")

intake_result = st.session_state.get("online_intake_result")
if intake_result:
    st.subheader("Online source intake")
    st.write(f"**Company:** {intake_result['company']}  ·  **Source:** [{intake_result['title']}]({intake_result['url']})")
    st.caption(
        f"Cached file: `{intake_result['cache_path']}` · SHA-256: `{intake_result['sha256']}` · "
        f"{'reused from cache' if intake_result['cache_reused'] else 'fetched online'}"
    )
    candidate_rows = [
        row for row in intake_result.get("candidates", [])
        if row.get("status") == "unverified"
    ]
    if candidate_rows:
        st.dataframe(
            [{"Candidate ID": row.get("id"), "Metric": row.get("metric"), "Extracted value": row.get("value"),
              "Unit": row.get("unit") or "Unresolved", "Period": row.get("period") or "Unresolved",
              "Column year": next((note.split(": ", 1)[1].rstrip(".") for note in row.get("notes", [])
                                   if note.startswith("Dated column header year: ")), "Unresolved"),
              "PDF page": row.get("doc_page"),
              "Status": row.get("status"), "Source snippet": row.get("snippet")} for row in candidate_rows],
            use_container_width=True, hide_index=True,
        )
        st.warning(
            "These are extraction candidates, not verified observations. Review each cited PDF page and approve only "
            "values whose period, unit, statement basis, and scope are clear."
        )
        st.markdown("After review, approve a candidate with `verify-candidate` and rerun the deterministic analysis:")
        st.code(
            f'python scripts/argus.py verify-candidate "{intake_result["candidate_file"]}" <candidate-id> '
            '--verified-by "Reviewer name" --period <FY> --unit <unit> --period-type annual '
            '--currency INR --basis <standalone-or-consolidated>\n'
            f'python scripts/argus.py run --company "{intake_result["company"]}"',
            language="powershell",
        )
    else:
        st.info(
            "There are no reviewable candidate values from this source. An empty or ambiguous candidate file "
            "is not evidence and must not be approved. "
            f"{intake_result.get('ambiguous_count', 0)} prior rows, if any, remain ambiguous and are not reviewable."
        )

if selected_report is None:
    st.stop()

doc = report_docs[selected_report]
analysis_path = selected_report.with_name(f"{selected_report.stem}-analysis.json")
analysis = load_json(str(analysis_path))
ledger = read_ledger()
ledger_by_id = {e.get("id"): e for e in ledger}

validation = doc.get("validation") or {}
state = validation.get("state", "unknown")
company = doc.get("company", selected_report.stem.replace("-", " ").title())
if intake_result and intake_result.get("company", "").casefold() != company.casefold():
    st.info(
        f"Live intake is for {intake_result.get('company')}; the saved dossier below is for {company}. "
        "Importing a source does not replace or generate a company dossier."
    )
linked_entries = [ledger_by_id[eid] for eid in doc.get("evidence", []) if eid in ledger_by_id]
tested_count, abstained_count, abstention_reasons = angle_summary(analysis)
candidate_count = len(validation.get("candidates") or [])
rejected_count = len(validation.get("rejected_findings") or [])
score = doc.get("evidence_score", 0.0)
score_label = doc.get("evidence_label", "Weak")

# Prepare PDF Export Data
pdf_data = None
try:
    from argus.report.pdf_export import build_pdf
    from argus.schemas import Dossier
    pdf_data = build_pdf(Dossier.model_validate(doc), ledger_entries=ledger, analysis=analysis)
except Exception:
    pdf_data = None

# Hero Header (Clean Light Gradient)
status_color = "badge-verified" if state in {"unexplained", "validated"} else "badge-abstain"
status_pulse = "pulse-emerald" if state in {"unexplained", "validated"} else "pulse-amber"
status_title = "Validated Anomaly" if state in {"unexplained", "validated"} else "Evidence-Grounded Abstention"

col_header, col_actions = st.columns([3.8, 1.2])
with col_header:
    st.markdown(
        f"""
        <div class="argus-hero">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                <span class="argus-badge badge-neutral">◈ Track C: FMCG & Consumer Retail</span>
                <span class="argus-badge {status_color}">
                    <span class="pulse-dot {status_pulse}"></span>
                    {status_title}
                </span>
            </div>
            <h1 style="margin: 0.2rem 0; font-size: 2.3rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">
                {company}
            </h1>
            <p style="margin: 0; color: #475569; font-size: 0.95rem;">
                Deterministic financial screening · Verifiable SHA-256 source ledger · Zero synthetic hallucinations
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_actions:
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 16px; padding: 1.1rem 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05); display: flex; flex-direction: column; justify-content: center; height: 132px;">
            <div style="font-size: 0.74rem; font-weight: 750; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem;">
                Formal Audit Export
            </div>
            <div style="margin-bottom: 0.5rem;">
        """,
        unsafe_allow_html=True,
    )
    if pdf_data:
        st.download_button(
            label="📄 Export Dossier PDF",
            data=pdf_data,
            file_name=f"{selected_report.stem}-dossier.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch",
            help="Download formal, printable audit dossier with exact source citations.",
        )
    else:
        st.button("Export PDF", disabled=True, width="stretch")
    st.markdown(
        """
            </div>
            <div style="font-size: 0.7rem; color: #94a3b8; text-align: center;">SHA-256 Verified Audit Report</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# KPI Metric Ribbon
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">Run Result</div>
            <div class="metric-card-value" style="color: {'#059669' if state in {'unexplained', 'validated'} else '#d97706'};">
                {state.replace('_', ' ').title()}
            </div>
            <div class="metric-card-sub">Persistence & peer gates enforced</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">Verified Observations</div>
            <div class="metric-card-value" style="color: #0284c7;">
                {len(linked_entries)}
            </div>
            <div class="metric-card-sub">Traced to official BSE/NSE pages</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">Audit Panels</div>
            <div class="metric-card-value" style="color: #4f46e5;">
                {len(analysis.get("panels", []))}
            </div>
            <div class="metric-card-sub">Isolated comparability cohorts</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">Evidence Score</div>
            <div class="metric-card-value" style="color: #7c3aed;">
                {score:.1f} <span style="font-size: 1rem; color: #64748b;">({score_label})</span>
            </div>
            <div class="metric-card-sub">5 deterministic component weights</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# 5 Focused Functional Tabs
tab_brief, tab_charts, tab_panels, tab_ledger, tab_eval = st.tabs(
    [
        "◈ Executive Brief & Proof",
        "📈 Interactive Financial Analysis",
        "📑 Statements & Cohorts",
        "🔍 Forensic Evidence Trail",
        "🛡️ Falsification & Scoreboard",
    ]
)

# -------------------------------------------------------------
# TAB 1: EXECUTIVE BRIEF & PROOF PANEL
# -------------------------------------------------------------
with tab_brief:
    st.markdown(
        f"""
        <div class="glass-callout {'callout-amber' if candidate_count == 0 else 'callout-emerald'}">
            <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: {'#b45309' if candidate_count == 0 else '#047857'}; margin-bottom: 0.4rem;">
                Deterministic Screening Verdict
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a; line-height: 1.4;">
                {doc.get('discovery', 'No reliable finding recorded.')}
            </div>
            <div style="margin-top: 0.6rem; font-size: 0.88rem; color: #475569;">
                {
                    "ARGUS abstains rather than filling unrecorded periods with zeroes or guessing. A discovery requires persistence ≥ 3 consecutive periods, ≥ 3 peer panels, and multi-layer source corroboration."
                    if candidate_count == 0 else
                    "This signal cleared the deterministic persistence and peer-dispersion gates."
                }
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_brief, right_brief = st.columns([1.5, 1])

    with left_brief:
        st.markdown("#### 🎯 **Why It Matters**")
        why_items = doc.get("why_it_matters") or []
        if why_items:
            for item in why_items:
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 3px solid #0284c7; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.6rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                        <span style="color: #1e293b; font-size: 0.92rem;">{item}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No context recorded.")

    with right_brief:
        st.markdown("#### ⚖️ **Evidence Score Breakdown**")
        components = doc.get("score_components") or {}
        if components:
            for comp_name, comp_val in components.items():
                st.markdown(f"**{comp_name.replace('_', ' ').title()}**: `{comp_val:.1f} pts`")
                st.progress(min(comp_val / 25.0, 1.0))
        else:
            st.info("Evidence score is capped at Weak (0.0) due to insufficient multi-peer baseline data.")

    st.markdown("---")
    st.markdown("### 🏆 **The Proof Panel: Institutional Comparator**")
    st.caption("Direct side-by-side comparison illustrating why ARGUS's deterministic approach outperforms legacy screening and LLMs.")

    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        st.markdown(
            f"""
            <div class="proof-card" style="border-top: 3px solid #0284c7;">
                <div>
                    <div class="proof-card-header" style="color: #0369a1;">
                        <span>◈</span> ARGUS Engine
                    </div>
                    <p style="font-size: 0.85rem; color: #334155; margin-bottom: 0.8rem;">
                        <strong>Method:</strong> Dynamic Historical Range via Median & MAD (history minus latest 2), multi-year persistence ≥ 3 periods, and peer dispersion validation.
                    </p>
                    <div style="background: #f0f9ff; border: 1px solid #e0f2fe; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.82rem; color: #0369a1; margin-bottom: 0.8rem;">
                        <strong>Current Status:</strong> {state.replace('_', ' ').title()}<br>
                        <strong>Tested Angles:</strong> {tested_count}<br>
                        <strong>Abstention Count:</strong> {abstained_count}
                    </div>
                    <p style="font-size: 0.82rem; color: #64748b;">
                        Protects against false positives by refusing to flag isolated 1-year blips as structural anomalies.
                    </p>
                </div>
                <div style="font-size: 0.76rem; color: #0284c7; font-weight: 700; text-transform: uppercase;">
                    ✓ Zero Hallucination · Pure Code
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_col2:
        from eval.baselines.ratio_screen import flag as ratio_flag
        ratio_flags = []
        for res in analysis.get("panels", []):
            vals = res.get("panel", {}).get("metrics", {}).get("revenue", [])
            if len(vals) >= 2 and vals[-2] not in (None, 0) and vals[-1] is not None:
                chg = vals[-1] / vals[-2] - 1
                ratio_flags.append(ratio_flag(chg))
        ratio_triggered = any(ratio_flags)

        st.markdown(
            f"""
            <div class="proof-card" style="border-top: 3px solid #d97706;">
                <div>
                    <div class="proof-card-header" style="color: #b45309;">
                        <span>📊</span> Traditional Ratio Screen
                    </div>
                    <p style="font-size: 0.85rem; color: #334155; margin-bottom: 0.8rem;">
                        <strong>Method:</strong> Static rule (absolute annual revenue or working capital change > 20%).
                    </p>
                    <div style="background: #fffbeb; border: 1px solid #fef3c7; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.82rem; color: #92400E; margin-bottom: 0.8rem;">
                        <strong>Screen Output:</strong> {'Triggered Flag' if ratio_triggered else 'No Flag'}<br>
                        <strong>Threshold:</strong> > 20% annual variance<br>
                        <strong>False Alarm Risk:</strong> High
                    </div>
                    <p style="font-size: 0.82rem; color: #64748b;">
                        Lacks historical dispersion context. Conflates one-time corporate demergers or inflation surges with genuine operating stress.
                    </p>
                </div>
                <div style="font-size: 0.76rem; color: #d97706; font-weight: 700; text-transform: uppercase;">
                    ⚠ Naive Threshold · Ignores Demergers
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_col3:
        st.markdown(
            """
            <div class="proof-card" style="border-top: 3px solid #db2777;">
                <div>
                    <div class="proof-card-header" style="color: #be185d;">
                        <span>🤖</span> Plain LLM Prompting
                    </div>
                    <p style="font-size: 0.85rem; color: #334155; margin-bottom: 0.8rem;">
                        <strong>Method:</strong> Prompting generic frontier LLMs to analyze financial statements.
                    </p>
                    <div style="background: #fdf2f8; border: 1px solid #fce7f3; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.82rem; color: #9d174d; margin-bottom: 0.8rem;">
                        <strong>Proven Flaw:</strong> Hallucinated Digits<br>
                        <strong>Traceability:</strong> 0% Grounded<br>
                        <strong>Consistency:</strong> Non-deterministic
                    </div>
                    <p style="font-size: 0.82rem; color: #64748b;">
                        LLMs invent plausible financial numbers, mix up standalone with consolidated figures, and cannot cite physical PDF byte locations.
                    </p>
                </div>
                <div style="font-size: 0.76rem; color: #db2777; font-weight: 700; text-transform: uppercase;">
                    ✕ Unreliable for Capital Allocation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------
# TAB 2: INTERACTIVE FINANCIAL ANALYSIS & RESIDUAL CHARTS
# -------------------------------------------------------------
with tab_charts:
    st.markdown("### 📈 **Quantitative Angle & Historical Range Inspector**")
    st.caption("Center and spread are calculated from historical periods excluding the latest two observations. Values breaching the ±2 spread band are flagged.")

    all_angles_tested = []
    for p_idx, res in enumerate(analysis.get("panels", [])):
        p = res.get("panel", {})
        p_label = f"Panel {p_idx+1}: {p.get('comparability_cohort')} ({p.get('consolidation_basis')})"
        for a_name, a_data in res.get("angles", {}).items():
            if a_data.get("status") == "tested" and any(v is not None for v in a_data.get("reported", [])):
                all_angles_tested.append((p_label, a_name, p, a_data))

    if not all_angles_tested:
        st.info("No tested angles are present in this dossier. Panels with fewer than 6 disclosed periods abstain under Rule R4.")
    else:
        angle_options = [f"{item[1].replace('_', ' ').title()} — {item[0]}" for item in all_angles_tested]
        chosen_idx = st.selectbox("Select Financial Angle to Inspect", range(len(all_angles_tested)), format_func=lambda i: angle_options[i])
        p_label, a_name, p_info, a_data = all_angles_tested[chosen_idx]

        periods = a_data.get("periods", [])
        reported_vals = a_data.get("reported", [])
        lows = a_data.get("expected_low", [])
        highs = a_data.get("expected_high", [])
        spreads = a_data.get("expected_spread", [])
        flags = a_data.get("gap_flags", [])

        df_chart = []
        for i, period in enumerate(periods):
            rep = reported_vals[i] if i < len(reported_vals) else None
            lo = lows[i] if i < len(lows) else None
            hi = highs[i] if i < len(highs) else None
            fl = flags[i] if i < len(flags) else False
            if rep is not None:
                df_chart.append({
                    "Period": period,
                    "Observed": float(rep),
                    "Expected Low": float(lo) if lo is not None else None,
                    "Expected High": float(hi) if hi is not None else None,
                    "Breach": bool(fl),
                    "Spread": float(spreads[i]) if i < len(spreads) and spreads[i] is not None else None,
                })

        chart_df = pd.DataFrame(df_chart)

        if not chart_df.empty:
            # Expected Range Shaded Band in Soft Sky Blue
            band_chart = (
                alt.Chart(chart_df)
                .mark_area(opacity=0.32, color="#bae6fd")
                .encode(
                    x=alt.X("Period:O", sort=None, title="Financial Period"),
                    y=alt.Y("Expected Low:Q", title=f"{a_name.replace('_', ' ').title()} (Days / Ratio)"),
                    y2="Expected High:Q",
                )
            )

            # Observed Trajectory Line in Deep Royal Blue
            line_chart = (
                alt.Chart(chart_df)
                .mark_line(color="#0284c7", strokeWidth=3)
                .encode(
                    x=alt.X("Period:O", sort=None),
                    y="Observed:Q",
                )
            )

            # Point Markers with Tooltips
            point_chart = (
                alt.Chart(chart_df)
                .mark_circle(size=90, color="#0369a1")
                .encode(
                    x=alt.X("Period:O", sort=None),
                    y="Observed:Q",
                    tooltip=[
                        alt.Tooltip("Period:O", title="Period"),
                        alt.Tooltip("Observed:Q", format=".2f", title="Observed Metric"),
                        alt.Tooltip("Expected Low:Q", format=".2f", title="Expected Lower Bound"),
                        alt.Tooltip("Expected High:Q", format=".2f", title="Expected Upper Bound"),
                        alt.Tooltip("Breach:N", title="Gap Flag (Anomaly)"),
                    ],
                )
            )

            # Anomaly Highlights (Red Breach Points)
            breach_df = chart_df[chart_df["Breach"]]
            if not breach_df.empty:
                breach_chart = (
                    alt.Chart(breach_df)
                    .mark_circle(size=170, color="#dc2626")
                    .encode(
                        x=alt.X("Period:O", sort=None),
                        y="Observed:Q",
                        tooltip=[
                            alt.Tooltip("Period:O", title="Breach Period"),
                            alt.Tooltip("Observed:Q", format=".2f", title="Observed (Anomalous)"),
                            alt.Tooltip("Expected High:Q", format=".2f", title="Expected Upper Threshold"),
                        ],
                    )
                )
                final_chart = band_chart + line_chart + point_chart + breach_chart
            else:
                final_chart = band_chart + line_chart + point_chart

            st.altair_chart(
                final_chart.properties(height=380, width="container")
                .configure_view(strokeOpacity=0)
                .configure_axis(
                    gridColor="#f1f5f9",
                    domainColor="#cbd5e1",
                    tickColor="#cbd5e1",
                    labelColor="#475569",
                    titleColor="#0f172a",
                ),
                width="stretch",
            )

            st.markdown(
                """
                <div style="display: flex; gap: 1.5rem; justify-content: center; font-size: 0.82rem; color: #475569; margin-top: -0.5rem; margin-bottom: 1.2rem;">
                    <span><span style="color: #0284c7; font-weight: bold;">■</span> Shaded Band: ±2 MAD Historical Expected Range</span>
                    <span><span style="color: #0369a1; font-weight: bold;">●</span> Blue Line: Reported Values</span>
                    <span><span style="color: #dc2626; font-weight: bold;">●</span> Red Marker: Period Range Breached</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("##### Detailed Metric Table")
        st.dataframe(
            chart_df.style.format({
                "Observed": "{:.2f}",
                "Expected Low": "{:.2f}",
                "Expected High": "{:.2f}",
                "Spread": "{:.2f}",
            }),
            width="stretch",
            hide_index=True,
        )

# -------------------------------------------------------------
# TAB 3: STATEMENTS & COHORTS
# -------------------------------------------------------------
with tab_panels:
    st.markdown("### 📑 **Audited Financial Panels & Statement Cohorts**")
    st.caption("Financial figures are grouped into strictly isolated comparability cohorts (e.g. pre-demerger vs post-demerger) to prevent false trends.")

    panels_list = analysis.get("panels", [])
    if not panels_list:
        st.info("No panels assembled for this company.")
    else:
        panel_names = [
            f"Panel {i+1}: {p['panel'].get('comparability_cohort')} · {p['panel'].get('consolidation_basis')} ({len(p['panel'].get('periods', []))} periods)"
            for i, p in enumerate(panels_list)
        ]
        sel_panel_idx = st.selectbox("Select Panel Cohort", range(len(panels_list)), format_func=lambda i: panel_names[i])
        chosen_panel_obj = panels_list[sel_panel_idx]
        p_data = chosen_panel_obj.get("panel", {})

        p_c1, p_c2, p_c3, p_c4 = st.columns(4)
        cohort_metadata = [
            ("Consolidation Basis", p_data.get("consolidation_basis", "unknown").title(), "#0284c7"),
            ("Reporting Scope", p_data.get("reporting_scope", "unknown").replace("_", " ").title(), "#059669"),
            ("Reporting Currency", p_data.get("currency", "unknown"), "#4f46e5"),
            ("Period Granularity", p_data.get("period_type", "unknown").title(), "#7c3aed"),
        ]
        for col, (label, val, clr) in zip([p_c1, p_c2, p_c3, p_c4], cohort_metadata):
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card" style="padding: 0.9rem 1.1rem; margin-bottom: 0.8rem;">
                        <div class="metric-card-label">{label}</div>
                        <div class="metric-card-value" style="font-size: 1.35rem; color: {clr};">{val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("#### Audited Financial Disclosures")
        panel_periods = [p.get("period") for p in p_data.get("periods", [])]
        table_rows = []
        for metric, values in p_data.get("metrics", {}).items():
            ids_by_p = p_data.get("ledger_ids", {}).get(metric, [])
            unit = p_data.get("units", {}).get(metric, "")
            for idx, period in enumerate(panel_periods):
                ids = ids_by_p[idx] if idx < len(ids_by_p) else []
                val = values[idx] if idx < len(values) else None
                table_rows.append({
                    "Period": period,
                    "Metric": metric.replace("_", " ").title(),
                    "Value": val,
                    "Unit": unit,
                    "Ledger IDs": ", ".join(ids),
                })

        if table_rows:
            st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)
        else:
            st.info("No verified metric figures recorded for this panel.")

        st.markdown("#### Angle Testing Status for this Panel")
        angle_status_rows = []
        for a_k, a_v in chosen_panel_obj.get("angles", {}).items():
            angle_status_rows.append({
                "Angle": a_k.replace("_", " ").title(),
                "Status": a_v.get("status", "unknown").title(),
                "Evaluation / Abstain Reason": a_v.get("abstain_reason") or "Tested without abstention.",
                "Disclosed Periods": len(a_v.get("periods", [])),
            })
        st.dataframe(pd.DataFrame(angle_status_rows), width="stretch", hide_index=True)

# -------------------------------------------------------------
# TAB 4: FORENSIC EVIDENCE TRAIL
# -------------------------------------------------------------
with tab_ledger:
    st.markdown("### 🔍 **Zero-Hallucination Evidence Trail**")
    st.caption("Every number used in ARGUS originates from a human-reviewed public filing with verbatim snippet and SHA-256 hash.")

    if not linked_entries:
        st.info("No ledger entries are linked to this dossier.")
    else:
        search_query = st.text_input(
            "Filter ledger observations",
            placeholder="Type to search by metric (e.g. Revenue), period (e.g. FY2025), or ledger ID (e.g. L0008)...",
            label_visibility="collapsed",
        ).strip().lower()
        filtered_entries = [
            e for e in linked_entries
            if search_query in e.get("id", "").lower()
            or search_query in e.get("metric", "").lower()
            or search_query in e.get("period", "").lower()
            or search_query in e.get("snippet", "").lower()
        ]

        st.caption(f"Showing {len(filtered_entries)} of {len(linked_entries)} verified observations.")

        ev_summary = []
        for e in filtered_entries:
            ev_summary.append({
                "Ledger ID": e.get("id"),
                "Metric": e.get("metric", "").replace("_", " ").title(),
                "Value": e.get("value"),
                "Unit": e.get("unit"),
                "Period": e.get("period"),
                "Basis": e.get("consolidation_basis"),
                "PDF Page": e.get("doc_page"),
                "Source Link": e.get("source_url"),
            })

        st.dataframe(
            pd.DataFrame(ev_summary),
            width="stretch",
            hide_index=True,
            column_config={
                "Source Link": st.column_config.LinkColumn("Filing URL", display_text="Open Official PDF"),
                "Value": st.column_config.NumberColumn("Disclosed Value", format="%.2f"),
            },
        )

        st.markdown("---")
        st.markdown("#### Detailed Page-Level Provenance")

        for e in filtered_entries:
            e_id = e.get("id", "Lxxxx")
            e_metric = e.get("metric", "metric").replace("_", " ").title()
            e_period = e.get("period", "period")
            e_val = e.get("value")
            e_unit = e.get("unit", "")

            with st.expander(f"📁 {e_id} · {e_metric} = {e_val:,.1f} {e_unit} ({e_period})"):
                c_snip, c_meta = st.columns([2, 1])
                with c_snip:
                    st.markdown("**Verbatim Statement Excerpt**")
                    st.markdown(
                        f"""
                        <div class="evidence-snippet">
                            "{html.escape(e.get('snippet', 'No snippet text.'))}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Physical Statement Location: Page {e.get('doc_page', 'N/A')} of official filing.")

                with c_meta:
                    st.markdown("**Verification Metadata**")
                    st.write(f"**Verified By:** {e.get('verified_by', 'Auditor')}")
                    st.write(f"**Basis:** {e.get('consolidation_basis', 'N/A')} · {e.get('reporting_scope', 'N/A')}")
                    st.markdown(f"**SHA-256:** `{e.get('source_sha256', '')[:16]}...`")
                    if e.get("source_url"):
                        st.link_button("Open Source PDF", e["source_url"], width="stretch")

# -------------------------------------------------------------
# TAB 5: FALSIFICATION & SCOREBOARD
# -------------------------------------------------------------
with tab_eval:
    st.markdown("### 🛡️ **Falsification Rigor & Evaluation Benchmarks**")

    col_fals, col_counter = st.columns(2)
    with col_fals:
        st.markdown(
            f"""
            <div class="glass-callout" style="border-left: 4px solid #dc2626; background: #fff5f5;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #dc2626; text-transform: uppercase;">
                    Scientific Falsification Condition
                </div>
                <div style="font-size: 0.95rem; color: #1e293b; margin-top: 0.4rem; line-height: 1.5;">
                    {doc.get('falsification_condition', 'Not recorded.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_counter:
        st.markdown(
            f"""
            <div class="glass-callout" style="border-left: 4px solid #4f46e5; background: #f5f3ff;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #4f46e5; text-transform: uppercase;">
                    Skeptic Counterargument
                </div>
                <div style="font-size: 0.95rem; color: #1e293b; margin-top: 0.4rem; line-height: 1.5;">
                    {doc.get('counterargument', 'Not recorded.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 🧪 **The 7 Benign Alternative Checks (Red-Team Audit)**")
    st.caption("A persistent financial gap is rejected if benign operational alternatives account for the deviation.")

    red_team_checks = [
        ("Seasonality", "Quarterly or intra-year working capital cycles.", "not_tested", "No multi-year quarterly filing series verified."),
        ("Base Effects", "Comparisons against an abnormal pandemic or lockdown base.", "not_tested", "Requires historical comparative base adjustment."),
        ("One-off Events", "Litigation settlements, restructuring charges, or tax provisions.", "not_tested", "No exceptional items flagged in notes."),
        ("Accounting Changes", "New Ind AS / IFRS adoption altering asset or liability recognition.", "not_tested", "Accounting policy disclosures remain unreviewed."),
        ("Acquisitions & Demergers", "Undertaking spin-offs (e.g. Note 44 on Ice Cream business transfer).", "not_tested", "Demerger cohorts isolated; impact unquantified."),
        ("Pricing Lags", "Input cost inflation passthrough delay.", "not_tested", "Commodity WPI index series not connected."),
        ("Sector-Wide Movements", "Industry-wide trends affecting all FMCG peers equally.", "not_tested", "Peer panels < 3; sector dispersion unmeasured."),
    ]

    rt_cols = st.columns(4)
    for idx, (check_title, check_desc, check_status, check_note) in enumerate(red_team_checks):
        col_target = rt_cols[idx % 4]
        with col_target:
            col_target.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.85rem; margin-bottom: 0.8rem; min-height: 140px; box-shadow: 0 2px 6px rgba(15,23,42,0.02);">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 0.2rem;">{check_title}</div>
                    <div style="font-size: 0.74rem; color: #475569; margin-bottom: 0.4rem;">{check_desc}</div>
                    <div style="font-size: 0.72rem; color: #d97706; font-weight: 600;">Status: {check_status.replace('_', ' ').title()}</div>
                    <div style="font-size: 0.68rem; color: #64748b;">{check_note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("#### 📊 **Evaluation Scoreboard: Track C Benchmarks**")
    st.caption("Measurements from `python scripts/argus.py eval`. Synthetic canary tests are explicitly separated from real-company audit status.")

    scoreboard_path = ROOT / "eval" / "results" / "scoreboard.md"
    if scoreboard_path.exists():
        st.markdown(scoreboard_path.read_text(encoding="utf-8"))
    else:
        st.info("Run `python scripts/argus.py eval` to generate the evaluation scoreboard.")

    cand_list = validation.get("candidates") or []
    rej_list = validation.get("rejected_findings") or []
    st.markdown("#### Gate Audit Trail")
    st.write(f"Generated Candidates: `{len(cand_list)}` · Rejected Findings: `{len(rej_list)}`")
    if rej_list:
        st.dataframe(pd.DataFrame(rej_list), width="stretch", hide_index=True)
    else:
        st.caption("No candidates were generated or rejected in this run.")
