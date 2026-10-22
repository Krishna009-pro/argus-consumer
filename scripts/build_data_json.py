import json
from pathlib import Path

reports_dir = Path("reports")
ledger_path = Path("data/ledger.jsonl")

# Load all ledger entries
ledger_entries = []
if ledger_path.exists():
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            ledger_entries.append(json.loads(line))

# Also add candidates from Nestle as ledger-style candidate entries so EvidenceTrail can link them
nestle_cand_path = Path("data/candidates/candidates-0cc21036eadc-07edd50b.json")
if nestle_cand_path.exists():
    nestle_cands = json.loads(nestle_cand_path.read_text(encoding="utf-8"))
    for c in nestle_cands:
        ledger_entries.append({
            "id": c.get("id"),
            "company": c.get("company", "Nestle India Limited"),
            "metric": c.get("metric"),
            "value": c.get("value"),
            "period": c.get("period") or "FY2025",
            "period_type": "annual",
            "period_start": "2024-04-01",
            "period_end": "2025-03-31",
            "unit": "INR_crore",
            "currency": "INR",
            "source_type": "filing",
            "source_url": c.get("source_url"),
            "source_sha256": c.get("source_sha256"),
            "cache_path": c.get("cache_path"),
            "doc_page": c.get("doc_page"),
            "snippet": c.get("snippet"),
            "notes": "Machine-extracted candidate from official NSE statutory filing (unverified)",
            "verified": False,
            "verified_by": None,
            "verified_at": None,
            "status": "unverified"
        })

reports = {}

# Map slugs to aliases
aliases = {
    "hindustan-unilever-limited": ["hul", "hindustan unilever", "hindustan unilever limited"],
    "itc-limited": ["itc", "itc limited"],
    "godrej-consumer-products-limited": ["godrej", "gcpl", "godrej consumer products", "godrej-consumer-products"],
    "nestle-india-limited": ["nestle", "nestle india", "nestle-india"],
    "united-spirits-limited": ["united-spirits", "united spirits", "usl", "mcdowell"],
    "britannia-industries-limited": ["britannia", "britannia industries", "britannia-industries"],
    "dabur-india-limited": ["dabur", "dabur india", "dabur-india"],
    "marico-limited": ["marico", "marico limited"]
}

for report_file in reports_dir.glob("*.json"):
    if report_file.name.endswith("-analysis.json") or report_file.name in ("rejected-findings.json", "rejected-findings.jsonl"):
        continue
    slug = report_file.stem
    analysis_file = reports_dir / f"{slug}-analysis.json"
    if not analysis_file.exists():
        continue
    
    dossier = json.loads(report_file.read_text(encoding="utf-8"))
    analysis = json.loads(analysis_file.read_text(encoding="utf-8"))
    
    report_data = {
        "dossier": dossier,
        "analysis": analysis
    }
    
    reports[slug] = report_data
    # Add alias mappings
    if slug in aliases:
        for alias in aliases[slug]:
            alias_slug = alias.lower().replace(" ", "-")
            reports[alias_slug] = report_data

bundle = {
    "ledger": ledger_entries,
    "reports": reports
}

out_path = Path("dashboard/src/data/data.json")
out_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
print(f"Generated {out_path} with {len(reports)} report keys and {len(ledger_entries)} ledger/candidate items.")
