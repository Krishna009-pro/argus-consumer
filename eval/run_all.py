"""Measure end-to-end company runs using the verified ledger as the universe."""
from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

from argus.ledger import EvidenceLedger
from argus.schemas import LedgerEntry

RESULT_PATH = Path("eval/results/run_all.json")


def _companies(entries: Iterable[LedgerEntry]) -> list[str]:
    companies: dict[str, str] = {}
    for entry in entries:
        if entry.company and entry.company.strip():
            companies.setdefault(entry.company.casefold(), entry.company.strip())
    return sorted(companies.values(), key=str.casefold)


def _implementation_digest() -> str:
    digest = hashlib.sha256()
    for path in (Path("src/argus/cli.py"), Path("src/argus/engine.py"),
                 Path("src/argus/panels.py"), Path(__file__)):
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def measure(entries: Iterable[LedgerEntry], run_fn: Callable[[str, list[LedgerEntry]], dict]) -> dict:
    """Run one cached analysis per distinct verified-ledger company and summarize outcomes."""
    rows = list(entries)
    companies = _companies(rows)
    results: list[dict] = []
    for company in companies:
        try:
            result = run_fn(company, rows)
            dossier = Path(result.get("dossier", ""))
            json_dossier = dossier.with_suffix(".json")
            analysis = dossier.with_name(f"{dossier.stem}-analysis.json")
            complete = bool(result.get("verified_entries", 0) > 0 and dossier.is_file()
                            and json_dossier.is_file() and analysis.is_file())
            results.append({**result, "complete": complete,
                            "error": None if complete else "analysis outputs or verified observations are missing"})
        except Exception as exc:  # keep failures visible without preventing other companies from running
            results.append({"company": company, "complete": False,
                            "error": f"{type(exc).__name__}: {exc}"})
    completed = sum(bool(row.get("complete")) for row in results)
    latencies = [float(row["elapsed_seconds"]) for row in results
                 if row.get("complete") and row.get("elapsed_seconds") is not None]
    return {
        "metric": "M05_companies_end_to_end",
        "M05_companies_end_to_end": completed,
        "M15_live_latency_seconds": statistics.median(latencies) if latencies else None,
        "company_count": len(companies),
        "completed_count": completed,
        "latency_sample_count": len(latencies),
        "companies": results,
        "status": "measured" if companies else "unavailable_no_verified_companies",
    }


def evaluate(*, ledger: EvidenceLedger | None = None,
             run_fn: Callable[[str, list[LedgerEntry]], dict] | None = None,
             output_path: str | Path = RESULT_PATH) -> dict:
    ledger = ledger or EvidenceLedger()
    entries = ledger.verified_entries()
    if run_fn is None:
        from argus.cli import run_company
        run_fn = run_company
    results = measure(entries, run_fn)
    results.update({
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "ledger_sha256": EvidenceLedger.sha256(ledger.path) if ledger.path.is_file() else None,
        "implementation_sha256": _implementation_digest(),
    })
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def latest_measurement(path: str | Path = RESULT_PATH,
                       ledger: EvidenceLedger | None = None) -> dict:
    """Expose a previous run only while its ledger and implementation inputs are unchanged."""
    ledger = ledger or EvidenceLedger()
    result_path = Path(path)
    if not result_path.is_file():
        return {"M05_companies_end_to_end": None, "M15_live_latency_seconds": None}
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        current_ledger_hash = EvidenceLedger.sha256(ledger.path) if ledger.path.is_file() else None
    except (OSError, json.JSONDecodeError):
        return {"M05_companies_end_to_end": None, "M15_live_latency_seconds": None}
    if (result.get("ledger_sha256") != current_ledger_hash
            or result.get("implementation_sha256") != _implementation_digest()):
        return {"M05_companies_end_to_end": None, "M15_live_latency_seconds": None}
    return {"M05_companies_end_to_end": result.get("M05_companies_end_to_end"),
            "M15_live_latency_seconds": result.get("M15_live_latency_seconds")}


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
