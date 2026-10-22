# ARGUS-Consumer: Complete Execution Plan (This Week)

**Goal**: Reach M05 target (6 companies), build M01 reconciliation, enable peer gates, prepare for real validation.

---

## Monday — Godrej Data Ingestion

### 1. Discover & Cache 6 Annual Reports (FY2020–FY2025)

```bash
# FY2025-26 (latest)
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url "https://godrejcp.com/annual-reports/fy2025-26.pdf"

# FY2024-25
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url "https://godrejcp.com/annual-reports/fy2024-25.pdf"

# FY2023-24
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url "https://godrejcp.com/annual-reports/fy2023-24.pdf"

# FY2022-23
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url "https://godrejcp.com/annual-reports/fy2022-23.pdf"

# FY2021-22
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url "https://godrejcp.com/annual-reports/fy2021-22.pdf"

# FY2020-21
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url "https://godrejcp.com/annual-reports/fy2020-21.pdf"
```

> **If company site lacks old reports**: Use BSE/NSE URLs:
> - `https://www.bseindia.com/xml-data/corpfiling/AttachHis/<filing_id>.pdf`
> - Search: `site:bseindia.com "Godrej Consumer" "Annual Report"`

### 2. Extract Candidates from Each PDF

```bash
# List cached files
ls data/cache/*.pdf

# Extract each (note the SHA256 from prepare-company output)
python scripts/argus.py extract data/cache/<sha256_fy25>.pdf > candidates_fy25.json
python scripts/argus.py extract data/cache/<sha256_fy24>.pdf > candidates_fy24.json
python scripts/argus.py extract data/cache/<sha256_fy23>.pdf > candidates_fy23.json
python scripts/argus.py extract data/cache/<sha256_fy22>.pdf > candidates_fy22.json
python scripts/argus.py extract data/cache/<sha256_fy21>.pdf > candidates_fy21.json
python scripts/argus.py extract data/cache/<sha256_fy20>.pdf > candidates_fy20.json
```

### 3. Review Candidates
Open each `candidates_fyXX.json` — identify rows for:
- `revenue` (Revenue from Operations)
- `inventory` (Inventories)
- `trade_receivables` (Trade Receivables)

**Verify each against PDF page**: value, unit, period, standalone basis.

---

## Tuesday — Manual Verification & Ledger Entry

### Template Command (Run 18 Times)

```bash
python scripts/argus.py record \
  --company "Godrej Consumer Products Limited" \
  --metric <revenue|inventory|trade_receivables> \
  --value <exact_number_no_commas> \
  --unit INR_crore \
  --period <FY2020|FY2021|FY2022|FY2023|FY2024|FY2025> \
  --source-url <pdf_url> \
  --source-type filing \
  --snippet "<exact line from PDF including column headers>" \
  --cache-path data/cache/<sha256>.pdf \
  --page <page_number> \
  --period-type annual \
  --currency INR \
  --basis standalone \
  --verified-by "Your Name 2026-10-21"
```

### 18 Entries Checklist

| Period | Revenue | Inventory | Trade Receivables |
|--------|---------|-----------|-------------------|
| FY2020 | ☐ | ☐ | ☐ |
| FY2021 | ☐ | ☐ | ☐ |
| FY2022 | ☐ | ☐ | ☐ |
| FY2023 | ☐ | ☐ | ☐ |
| FY2024 | ☐ | ☐ | ☐ |
| FY2025 | ☐ | ☐ | ☐ |

**Critical**: All entries must be `consolidation_basis: standalone`. Confirm from PDF statement header.

---

## Wednesday — Verify Peer Gate Opens

```bash
python scripts/argus.py run --company "Hindustan Unilever Limited"
```

**Check output**: `reports/hindustan-unilever-limited-analysis.json`

```json
{
  "panels": [
    {
      "panel": {
        "comparability_cohort": "pre_demerger_standalone_FY2020_FY2025",
        "peer_companies": [
          "ITC Limited",
          "Britannia Industries Limited",
          "Marico Limited",
          "Godrej Consumer Products Limited"
        ]
      }
    }
  ]
}
```

**Success**: Pre-demerger panel shows **4 peer companies** (was 3).

Repeat for ITC, Britannia, Marico, Dabur — each should now show 4 peers.

---

## Thursday — Build Reconciliation Catalog

### Create `config/reconciliation.yaml`

```yaml
reconciliation_cases:
  # HUL: 6 periods × 2 metrics = 12 cases
  - company: "Hindustan Unilever Limited"
    period: "FY2020"
    published_metric: "receivable_days"
    published_value: <from_annual_report_ratio_table>
    published_formula: "Trade Receivables / Revenue * 365"
    published_source:
      url: "https://www.bseindia.com/xml-data/corpfiling/AttachHis/68482500696.pdf"
      page: 65
      snippet: "<exact line showing Receivable Days>"
    argus_computation:
      metric: "receivable_days"
      denominator: "revenue"
      scope: "company_total_operations"
      basis: "standalone"
    match_rule: "direct value comparison"

  - company: "Hindustan Unilever Limited"
    period: "FY2020"
    published_metric: "inventory_days"
    published_value: <from_annual_report_ratio_table>
    published_formula: "Inventory / Revenue * 365"
    published_source:
      url: "https://www.bseindia.com/xml-data/corpfiling/AttachHis/68482500696.pdf"
      page: 65
      snippet: "<exact line showing Inventory Days>"
    argus_computation:
      metric: "inventory_days"
      denominator: "revenue"
      scope: "company_total_operations"
      basis: "standalone"
    match_rule: "direct value comparison"

  # Repeat for FY2021, FY2022, FY2023, FY2024, FY2025 (same sources, different pages)
  # HUL FY2021: page 65-66, FY2022: page 71-72, FY2023: page 102-103, FY2024: page 139-140, FY2025: page 145-146

  # ITC: 6 periods × 2 metrics = 12 cases (FY2018–FY2024 continuing ops)
  - company: "ITC Limited"
    period: "FY2024"
    published_metric: "receivable_days"
    published_value: <value>
    published_formula: "Trade Receivables / Revenue * 365"
    published_source:
      url: "https://itcportal.com/content/dam/itc-corporate/open-pdfs/report-and-accounts/ITC-Report-and-Accounts-2024.pdf"
      page: <ratio_table_page>
      snippet: "<exact line>"
    argus_computation:
      metric: "receivable_days"
      denominator: "revenue"
      scope: "continuing_operations"
      basis: "standalone"
    match_rule: "direct value comparison"

  # Britannia: 6 periods × 2 metrics = 12 cases
  # Marico: 6 periods × 2 metrics = 12 cases
  # Dabur: 6 periods × 1 metric (inventory_turnover only where scope matches) + 6 receivable_days = ~7 cases
  # GCPL: 6 periods × 2 metrics = 12 cases

  # TOTAL: ~55 cases (target: ≥24 compared)
```

### How to Find Published Ratios
1. Open each company's annual report PDF
2. Search for "Ratio Analysis", "Key Ratios", "Financial Highlights"
3. Look for: **Receivable Days**, **Inventory Days**, **Inventory Turnover**
4. **Copy exact formula** from the report's definition (usually in notes)
5. **Copy exact value** and **page number**
6. **Only include if formula matches ARGUS**:
   - ARGUS `receivable_days` = `trade_receivables / revenue * days_in_period`
   - ARGUS `inventory_days` = `inventory / revenue * days_in_period` (when COGS unavailable)
   - If report uses `COGS` or `Average Inventory` → **exclude** or note mismatch

---

## Friday — Implement & Run M01 Reconciliation

### Replace `eval/reconcile.py`

```python
# eval/reconcile.py
from pathlib import Path
import yaml
from argus.ledger import EvidenceLedger
from argus.panels import build_company_panels, derive_angle_series

def evaluate() -> dict:
    catalog = yaml.safe_load(Path("config/reconciliation.yaml").read_text())["reconciliation_cases"]
    ledger = EvidenceLedger()
    entries = ledger.verified_entries()
    matched = compared = 0
    details = []
    for case in catalog:
        panels = build_company_panels(entries, case["company"])
        target_panel = next((p for p in panels
                             if p["consolidation_basis"] == case["argus_computation"]["basis"]
                             and p["reporting_scope"] == case["argus_computation"]["scope"]), None)
        if not target_panel:
            details.append({**case, "status": "no_compatible_panel"})
            continue
        angles = derive_angle_series(target_panel)
        angle = angles.get(case["argus_computation"]["metric"])
        if not angle or angle["status"] != "tested":
            details.append({**case, "status": "angle_not_tested"})
            continue
        try:
            period_idx = angle["periods"].index(case["period"])
        except ValueError:
            details.append({**case, "status": "period_not_in_panel"})
            continue
        argus_val = angle["reported"][period_idx]
        if argus_val is None:
            details.append({**case, "status": "missing_value"})
            continue
        # Apply match rule
        if case["match_rule"] == "direct value comparison":
            diff_pct = abs(argus_val - case["published_value"]) / case["published_value"] * 100
            ok = diff_pct <= 0.5 or abs(argus_val - case["published_value"]) <= 1
        elif case["match_rule"] == "recompute turnover":
            turnover = 365 / argus_val
            diff_pct = abs(turnover - case["published_value"]) / case["published_value"] * 100
            ok = diff_pct <= 0.5 or abs(turnover - case["published_value"]) <= 1
        else:
            ok = False
        compared += 1
        if ok:
            matched += 1
        details.append({**case, "argus_value": round(argus_val, 4), "match": ok, "status": "compared"})
    rate = 100 * matched / compared if compared else None
    return {
        "M01_reconciliation_rate": rate,
        "matched": matched,
        "compared": compared,
        "details": details,
        "status": "measured" if compared else "unavailable_no_cases"
    }

if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2))
```

### Run Full Evaluation

```bash
python scripts/argus.py eval
```

**Check `eval/results/scoreboard.md`**:
```
| M01_reconciliation_rate | XX.X | 90 | 95 | 99 | FLOOR/TARGET/BEYOND |
| M05_companies_end_to_end | 6    | 4  | 6  | 9  | TARGET              |
```

---

## Saturday — Volume Scope Audit

### Create `data/volume_scope_notes.md`

```markdown
# Volume Growth Scope Matching Audit

## Hindustan Unilever Limited
- **Revenue scope**: Company-wide (standalone pre-demerger FY2020-25)
- **Volume disclosure**: "Underlying Volume Growth - India Business" (quarterly presentations)
- **Match**: NO — India-only vs company-wide
- **Decision**: ABSTAIN price_volume angle
- **Source**: HUL Q4 FY2025 presentation, slide 12

## ITC Limited
- **Revenue scope**: Continuing Operations (standalone, post-hotels demerger)
- **Volume disclosure**: Check FMCG segment volume in investor presentations
- **Match**: TBD — verify FMCG revenue = FMCG volume perimeter
- **Decision**: PENDING
- **Source**: [Link to presentation]

## Britannia Industries Limited
- **Revenue scope**: Standalone total operations
- **Volume disclosure**: "Volume growth" in annual report / investor deck
- **Match**: TBD
- **Decision**: PENDING

## Marico Limited
- **Revenue scope**: Standalone (India + International)
- **Volume disclosure**: "Volume growth" by segment (India, International)
- **Match**: TBD — need consolidated volume matching consolidated revenue
- **Decision**: PENDING

## Dabur India Limited
- **Revenue scope**: Standalone (ex-Badshah Masala post-FY2023)
- **Volume disclosure**: Check investor presentations
- **Match**: TBD
- **Decision**: PENDING

## Godrej Consumer Products Limited
- **Revenue scope**: Standalone (India + GAUM + Other)
- **Volume disclosure**: "Volume growth" in investor presentations
- **Match**: TBD — verify if GAUM volume included or India-only
- **Decision**: PENDING
```

### Only Add `volume_growth` Ledger Entries Where:
1. Volume metric covers **same legal entity** (standalone/consolidated)
2. Volume metric covers **same geographies/segments** as revenue
3. Volume metric covers **same period definition** (FY vs CY)
4. Reviewer documents all three with PDF page references

---

## Sunday — Red-Team Evidence Templates

### Create Directory & 7 Template Files

```bash
mkdir -p data/redteam_templates
```

### Template: `data/redteam_templates/seasonality.json`
```json
{
  "check_id": "seasonality",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 12,
    "snippet": "Exact text showing seasonal pattern (e.g., 'Q4 typically 35% of annual sales')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 15.5,
  "amount_unit": "days"
}
```

### Template: `data/redteam_templates/base_effect.json`
```json
{
  "check_id": "base_effect",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 8,
    "snippet": "Exact text showing prior-period anomaly (e.g., 'FY2024 receivables elevated due to GST transition')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 12.0,
  "amount_unit": "days"
}
```

### Template: `data/redteam_templates/one_off_event.json`
```json
{
  "check_id": "one_off_event",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 44,
    "snippet": "Exact text describing one-off event (e.g., 'Fire at factory impacted Q2 production')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 8.0,
  "amount_unit": "days"
}
```

### Template: `data/redteam_templates/accounting_change.json`
```json
{
  "check_id": "accounting_change",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 52,
    "snippet": "Exact text describing accounting policy change (e.g., 'Adopted Ind AS 115, revenue recognition changed')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 20.0,
  "amount_unit": "days"
}
```

### Template: `data/redteam_templates/acquisition.json`
```json
{
  "check_id": "acquisition",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 38,
    "snippet": "Exact text describing acquisition/demerger (e.g., 'Acquired 51% of Badshah Masala effective July 2022')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 25.0,
  "amount_unit": "days"
}
```

### Template: `data/redteam_templates/pricing_lag.json`
```json
{
  "check_id": "pricing_lag",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 15,
    "snippet": "Exact text describing pricing lag (e.g., 'Raw material cost increases passed through with 2-quarter lag')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 10.0,
  "amount_unit": "days"
}
```

### Template: `data/redteam_templates/sector_trend.json`
```json
{
  "check_id": "sector_trend",
  "outcome": "supported|disconfirmed|unresolved",
  "reason": "Reviewer note citing source",
  "sources": [{
    "source_url": "https://...",
    "cache_path": "data/cache/<sha256>.pdf",
    "source_sha256": "<sha256>",
    "page": 22,
    "snippet": "Exact text showing sector-wide movement (e.g., 'Industry receivable days increased 15% due to credit tightening')",
    "review_status": "verified",
    "reviewed_by": "Name 2026-10-25"
  }],
  "benign_explained_amount": 30.0,
  "amount_unit": "days"
}
```

---

## Quick Reference: All Commands

```bash
# Monday: Cache & extract
python scripts/argus.py prepare-company --company "Godrej Consumer Products Limited" --url <URL>
python scripts/argus.py extract data/cache/<sha>.pdf > candidates.json

# Tuesday: Record (18x)
python scripts/argus.py record --company "Godrej Consumer Products Limited" --metric revenue --value <x> --unit INR_crore --period FY2025 --source-url <url> --source-type filing --snippet "<text>" --cache-path data/cache/<sha>.pdf --page <n> --period-type annual --currency INR --basis standalone --verified-by "Name 2026-10-21"

# Wednesday: Verify
python scripts/argus.py run --company "Hindustan Unilever Limited"

# Thursday: Edit config/reconciliation.yaml (55 cases)

# Friday: Replace eval/reconcile.py, then
python scripts/argus.py eval

# Saturday: Edit data/volume_scope_notes.md

# Sunday: Create data/redteam_templates/*.json (7 files)
```

---

## Definition of Done (Sunday EOD)

- [ ] Godrej: 18 verified ledger entries in `data/ledger.jsonl`
- [ ] HUL panel shows 4 peers in analysis JSON
- [ ] `config/reconciliation.yaml` has ≥24 cases with exact formula/page/snippet
- [ ] `eval/reconcile.py` runs → M01 rate with matched/compared counts
- [ ] `eval/results/scoreboard.md` shows M05=6 (TARGET) and M01 measured
- [ ] `data/volume_scope_notes.md` documents scope match/mismatch for all 6 companies
- [ ] `data/redteam_templates/` has 7 JSON templates ready to fill

---

## What NOT To Do This Week

| ❌ Don't | Why |
|----------|-----|
| Add LangGraph / LLM wiring | No candidate to test it on |
| Tune thresholds | Gates are spec constraints; abstention is correct |
| Dashboard features (Proof Panel, Living Findings) | Empty state until candidate exists |
| New angle modules | Volume/price blocked by scope mismatch |
| Automate extraction further | Manual verification is the gate (R4, R5) |

**The only path to a finding: verified data → peer gate → reconciliation → candidate → red-team → blind review. Execute the data steps above.**