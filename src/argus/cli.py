from __future__ import annotations
import argparse, json, re, sys, time
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit
from .ledger import EvidenceLedger
from .schemas import Dossier
from .report.dossier import abstention_dossier, render
from .canary import run as run_canary
from .engine import run_engine, make_dossier

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "company"

def run_company(company: str) -> dict:
    started = time.perf_counter()
    ledger = EvidenceLedger()
    entries = ledger.verified_entries()
    analysis = run_engine(entries, company)
    dossier = make_dossier(analysis, entries)
    dossier.validation["verified_ledger_entries"] = len([e for e in entries if e.company and e.company.casefold() == company.casefold()])
    dossier.validation["elapsed_seconds"] = round(time.perf_counter() - started, 4)
    output_dir = Path("reports"); output_dir.mkdir(exist_ok=True)
    path = output_dir / f"{slug(company)}.md"
    path.write_text(render(dossier), encoding="utf-8")
    (output_dir / f"{slug(company)}.json").write_text(dossier.model_dump_json(indent=2), encoding="utf-8")
    (output_dir / f"{slug(company)}-analysis.json").write_text(json.dumps(analysis, indent=2, allow_nan=False, default=str), encoding="utf-8")
    rejected_path = output_dir / "rejected-findings.jsonl"
    if analysis["rejected"]:
        with rejected_path.open("a", encoding="utf-8") as f:
            for item in analysis["rejected"]: f.write(json.dumps(item, allow_nan=False) + "\n")
    return {"company": company, "status": dossier.validation.get("state", "no_reliable_finding"), "dossier": str(path),
      "verified_entries": dossier.validation["verified_ledger_entries"], "panel_count": len(analysis["panels"]),
      "rejected_candidates": len(analysis["rejected"]), "elapsed_seconds": dossier.validation["elapsed_seconds"]}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="argus", description="Evidence-grounded public-data financial discovery")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run analysis for a company (abstains when inputs are insufficient)")
    run.add_argument("--company", required=True)
    ev = sub.add_parser("eval", help="Run deterministic evaluations")
    ing = sub.add_parser("cache", help="Fetch and cache a public source file")
    ing.add_argument("url")
    record = sub.add_parser("record", help="Record a verified public value from a cached source")
    record.add_argument("--company", required=True); record.add_argument("--metric", required=True)
    record.add_argument("--value", required=True, type=float); record.add_argument("--unit", required=True)
    record.add_argument("--period", required=True); record.add_argument("--source-url", required=True)
    record.add_argument("--source-type", required=True, choices=["filing", "management", "outside"])
    record.add_argument("--snippet", required=True); record.add_argument("--cache-path", required=True)
    record.add_argument("--page", type=int, required=True, help="PDF page containing the exact source table")
    record.add_argument("--period-type", required=True, choices=["annual", "quarter", "half_year", "nine_months", "other"])
    record.add_argument("--currency", required=True, help="Currency code, or N/A for non-currency metrics")
    record.add_argument("--basis", required=True, choices=["consolidated", "standalone", "unknown"])
    record.add_argument("--verified-by", required=True, help="Human reviewer who checked source table and context")
    record.add_argument("--period-start"); record.add_argument("--period-end"); record.add_argument("--denominator")
    record.add_argument("--reporting-scope"); record.add_argument("--comparability-cohort"); record.add_argument("--comparability-note")
    local = sub.add_parser("import-local", help="Cache a local PDF/CSV as unverified public-data candidates")
    local.add_argument("file"); local.add_argument("--company", required=True); local.add_argument("--source-url", required=True)
    local.add_argument("--source-type", choices=["filing", "management", "outside"], default="filing")
    review = sub.add_parser("verify-candidate", help="Manually approve one extraction candidate into the ledger")
    review.add_argument("candidate_file"); review.add_argument("candidate_id"); review.add_argument("--verified-by", required=True)
    review.add_argument("--period", required=True); review.add_argument("--unit", required=True)
    review.add_argument("--period-type", required=True, choices=["annual", "quarter", "half_year", "nine_months", "other"])
    review.add_argument("--currency", required=True); review.add_argument("--basis", required=True, choices=["consolidated", "standalone", "unknown"])
    review.add_argument("--period-start"); review.add_argument("--period-end"); review.add_argument("--denominator")
    review.add_argument("--reporting-scope"); review.add_argument("--comparability-cohort"); review.add_argument("--comparability-note")
    extract = sub.add_parser("extract", help="Print conservative value candidates from a cached PDF")
    extract.add_argument("cache_path")
    search = sub.add_parser("search-web", help="Discover public source URLs using the optional Serper API")
    search.add_argument("--query", required=True, help="Search query; results are suggestions, not verified evidence")
    search.add_argument("--limit", type=int, default=10)
    prepare = sub.add_parser("prepare-company", help="Discover and fetch an annual-report PDF into the unverified review queue")
    prepare.add_argument("--company", required=True)
    prepare.add_argument("--url", help="Use a known public report URL instead of web search")
    prepare.add_argument("--result", type=int, help="Select a 1-based search result when auto-selection is ambiguous")
    prepare.add_argument("--limit", type=int, default=10)
    pdf = sub.add_parser("export-pdf", help="Export a generated company dossier to PDF")
    pdf.add_argument("--company", required=True)
    pdf.add_argument("--output", type=Path, help="Optional destination path for the readable PDF")
    args = parser.parse_args(argv)
    if args.command == "run":
        print(json.dumps(run_company(args.company), indent=2)); return 0
    if args.command == "cache":
        from .ingest.cache import fetch
        try: path, digest = fetch(args.url)
        except RuntimeError as exc: parser.error(str(exc))
        print(json.dumps({"cache_path": str(path), "sha256": digest, "url": args.url}, indent=2)); return 0
    if args.command == "record":
        from datetime import datetime, timezone
        from .schemas import LedgerEntry
        cache_path = Path(args.cache_path)
        from .ingest.source_text import snippet_is_cached, snippet_contains_value
        if not snippet_is_cached(cache_path, args.snippet, args.page):
            raise SystemExit("The provided snippet does not exactly occur in the cached source; no ledger entry was written.")
        ledger = EvidenceLedger()
        if not snippet_contains_value(args.snippet, args.value):
            raise SystemExit("The supporting snippet does not contain the supplied value; no ledger entry was written.")
        entry = LedgerEntry(id=ledger.next_id(), metric=args.metric, value=args.value, unit=args.unit, period=args.period,
          source_url=args.source_url, source_type=args.source_type, doc_page=args.page, snippet=args.snippet,
          source_sha256=ledger.sha256(cache_path), retrieved_at=datetime.now(timezone.utc), cache_path=str(cache_path), company=args.company,
          period_type=args.period_type, period_start=args.period_start, period_end=args.period_end, currency=args.currency,
          consolidation_basis=args.basis, verified=True, verified_by=args.verified_by, verified_at=datetime.now(timezone.utc), denominator=args.denominator,
          reporting_scope=args.reporting_scope, comparability_cohort=args.comparability_cohort, comparability_note=args.comparability_note)
        ledger.append(entry)
        print(entry.model_dump_json(indent=2)); return 0
    if args.command == "import-local":
        from .ingest.local_import import import_local, save_candidates
        cache_path, candidates = import_local(args.file, company=args.company, source_url=args.source_url, source_type=args.source_type)
        candidate_file = save_candidates(candidates)
        review_summary = _candidate_review_summary(candidates)
        print(json.dumps({"cache_path": str(cache_path), "sha256": EvidenceLedger.sha256(cache_path),
          "candidate_file": str(candidate_file), "candidate_count": len(candidates),
          **review_summary, "newly_verified_count": 0}, indent=2)); return 0
    if args.command == "verify-candidate":
        from .ingest.local_import import verify_candidate
        entry = verify_candidate(args.candidate_file, args.candidate_id, verified_by=args.verified_by, period=args.period,
          unit=args.unit, period_type=args.period_type, currency=args.currency, consolidation_basis=args.basis,
          period_start=args.period_start, period_end=args.period_end, denominator=args.denominator,
          reporting_scope=args.reporting_scope, comparability_cohort=args.comparability_cohort, comparability_note=args.comparability_note)
        print(entry.model_dump_json(indent=2)); return 0
    if args.command == "extract":
        from .ingest.pdf_tables import extract as extract_pdf
        print(json.dumps(extract_pdf(args.cache_path), indent=2)); return 0
    if args.command == "search-web":
        from .search import search_serper, SearchConfigurationError
        try:
            results = search_serper(args.query, limit=args.limit)
        except (SearchConfigurationError, RuntimeError, ValueError) as exc:
            raise SystemExit(str(exc))
        print(json.dumps({"query": args.query, "status": "discovery_only_unverified", "results": results}, indent=2))
        return 0
    if args.command == "prepare-company":
        from .ingest.local_import import import_remote_pdf
        source_title = None
        search_results = []
        if args.url:
            source_url = args.url
            selection_status = "user_supplied_url_unverified"
        else:
            from .search import search_serper, SearchConfigurationError
            query = f'"{args.company}" annual report financial statements PDF'
            try:
                search_results = search_serper(query, limit=args.limit)
            except (SearchConfigurationError, RuntimeError, ValueError) as exc:
                raise SystemExit(str(exc))
            if args.result is not None:
                if not 1 <= args.result <= len(search_results):
                    raise SystemExit(f"--result must be between 1 and {len(search_results)}.")
                selected = search_results[args.result - 1]
                source_url, source_title = selected["url"], selected["title"]
                selection_status = "selected_search_result_unverified"
            else:
                annual_pdf_results = [(i, item) for i, item in enumerate(search_results, start=1)
                    if "annual report" in item["title"].casefold()
                    and urlsplit(item["url"]).path.casefold().endswith(".pdf")]
                if not annual_pdf_results:
                    print(json.dumps({"company": args.company, "status": "source_selection_required",
                      "query": query, "results": search_results,
                      "next_step": "Choose a public PDF report URL and rerun with --url, or choose a result number with --result."}, indent=2))
                    return 0
                _, selected = annual_pdf_results[0]
                source_url, source_title = selected["url"], selected["title"]
                selection_status = "search_ranked_annual_report_pdf_unverified"
        try:
            cache_path, digest, candidate_path, candidates, cache_reused = import_remote_pdf(source_url, company=args.company)
        except (OSError, ValueError, RuntimeError) as exc:
            raise SystemExit(str(exc))
        review_summary = _candidate_review_summary(candidates)
        print(json.dumps({"company": args.company, **review_summary,
          "source_url": source_url, "source_title": source_title, "source_selection": selection_status,
          "retrieval_mode": "existing_hash_verified_cache" if cache_reused else "fetched_to_hash_verified_cache",
          "cache_path": str(cache_path), "sha256": digest, "candidate_file": str(candidate_path),
          "candidate_count": len(candidates), "newly_verified_count": 0,
          "candidates": [{"id": c.id, "metric": c.metric, "value": c.value, "unit": c.unit,
            "period": c.period, "doc_page": c.doc_page, "status": c.status, "snippet": c.snippet}
            for c in candidates]}, indent=2))
        return 0
    if args.command == "export-pdf":
        from .report.pdf_export import build_pdf
        dossier_path = Path("reports") / f"{slug(args.company)}.json"
        if not dossier_path.is_file(): raise SystemExit(f"Run analysis first; dossier not found: {dossier_path}")
        dossier = Dossier.model_validate_json(dossier_path.read_text(encoding="utf-8"))
        ledger_entries = EvidenceLedger().verified_entries()
        analysis_path = Path("reports") / f"{slug(args.company)}-analysis.json"
        analysis = json.loads(analysis_path.read_text(encoding="utf-8")) if analysis_path.is_file() else None
        output = args.output or (Path("reports") / f"{slug(args.company)}.pdf")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(build_pdf(dossier, ledger_entries=ledger_entries, analysis=analysis))
        print(json.dumps({"pdf": str(output), "bytes": output.stat().st_size}, indent=2)); return 0
    if args.command == "eval":
        from eval.canary.missing_data import evaluate as missing
        from eval.rerun_check import evaluate as rerun
        from eval.stability import evaluate as stability
        from eval.reconcile import evaluate as reconcile
        from eval.grounding import evaluate as grounding
        from eval.baselines.score import evaluate as baselines
        ground = grounding()
        results = {**run_canary(), **missing(), **rerun(), **stability(),
                   "M02_claim_grounding_rate": ground["M02_claim_grounding_rate"],
                   "M03_unsupported_claims": ground["M03_unsupported_claims"],
                   "reconciliation": reconcile(), "grounding": ground, "baselines": baselines()}
        out = Path("eval/results"); out.mkdir(parents=True, exist_ok=True)
        (out / "summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        (out / "scoreboard.md").write_text(scoreboard(results), encoding="utf-8")
        print(json.dumps(results, indent=2)); print(f"Scoreboard: {out / 'scoreboard.md'}"); return 0
    return 2


def _candidate_review_summary(candidates) -> dict:
    """Describe persisted review states separately from approvals in this run."""
    counts = Counter(candidate.status for candidate in candidates)
    unresolved = sum(count for status, count in counts.items() if status != "verified")
    if not candidates:
        status = "no_candidates_extracted"
    elif unresolved:
        status = "candidates_present_review_required"
    else:
        status = "candidates_already_reviewed"
    return {
        "status": status,
        "verified_candidate_count": counts.get("verified", 0),
        "unresolved_candidate_count": unresolved,
        "candidate_status_counts": {name: counts.get(name, 0) for name in ("verified", "unverified", "ambiguous", "missing")},
    }

def scoreboard(results: dict) -> str:
    import yaml
    registry = yaml.safe_load(Path("config/metrics.yaml").read_text(encoding="utf-8"))["metrics"]
    lines = ["# ARGUS Evaluation Scoreboard", "", "Synthetic and unavailable results are labelled; bounds are targets, not outcomes.", "",
             "| ID | value | lower | target | stretch | tier |", "|---|---:|---:|---:|---:|---|"]
    for metric in registry:
        value = results.get(metric["id"])
        if value is None: tier = "UNAVAILABLE"
        elif metric.get("direction") == "band": tier = "IN_BAND" if metric["band"][0] <= value <= metric["band"][1] else "OUT_OF_BAND"
        elif metric.get("lower") == metric.get("target") == metric.get("stretch"):
            tier = "TARGET" if value == metric["target"] else "BELOW_FLOOR" if metric["direction"] == "higher_better" and value < metric["lower"] else "BELOW_FLOOR" if metric["direction"] == "lower_better" and value > metric["lower"] else "BEYOND"
        elif metric["direction"] == "higher_better": tier = "BEYOND" if value >= metric["stretch"] else "TARGET" if value >= metric["target"] else "FLOOR" if value >= metric["lower"] else "BELOW_FLOOR"
        else: tier = "BEYOND" if value <= metric["stretch"] else "TARGET" if value <= metric["target"] else "FLOOR" if value <= metric["lower"] else "BELOW_FLOOR"
        lines.append(f"| {metric['id']} | {value if value is not None else '—'} | {metric.get('lower', '—')} | {metric.get('target', '—')} | {metric.get('stretch', '—')} | {tier} |")
    lines += ["", "M07–M09 are synthetic canary measurements. Missing empirical datasets and human blind reviews remain unavailable."]
    return "\n".join(lines) + "\n"

if __name__ == "__main__": raise SystemExit(main())
