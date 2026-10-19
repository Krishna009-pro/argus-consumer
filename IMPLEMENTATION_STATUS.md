# ARGUS-Consumer implementation status

Updated 2026-10-19 from the current ledger, generated analyses, tests, and dashboard run. Detection thresholds were not changed. The working tree is a Git repository; the dashboard import-path fix is committed as `992eab9` and pushed to `origin/main`.

## Current verified-data results

| Company | Verified observations | Panels | Generated candidates | Rejected candidates | Current result |
|---|---:|---:|---:|---:|---|
| Hindustan Unilever Limited | 30 | 7 | 0 | 0 | `no_reliable_finding` |
| ITC Limited | 31 | 13 | 0 | 0 | `no_reliable_finding` |

HUL has one six-period standalone, pre-demerger panel with FY2020–FY2025 revenue, inventory, and trade receivables. Receivables-days has one flagged period (FY2025); the unchanged persistence rule requires three consecutive flagged periods, so no candidate is generated. Inventory-days remains within its expected range. The FY2025–FY2026 continuing-operations revenue and balance-sheet cohorts are kept separate from the pre-demerger series.

ITC has one four-period standalone, pre-demerger panel (FY2020–FY2023) with revenue, inventory, and receivables. Its newer continuing/discontinued-operation observations and balance sheets remain in separate cohorts. ITC is identified as a structurally eligible HUL peer in compatible panels, but no peer angle has six usable periods, so there are no peer-gap observations for the gate.

Both companies currently abstain. HUL price/volume lacks a verified, scope-matched volume series; its other abstentions cite missing matched inputs or fewer than six periods. ITC's four-period historical panel is below the six-period minimum. No missing value was replaced with zero. No company-specific logic was added to the analysis engine.

Detailed HUL page-level source review and coverage are in [hul-phase2-review.md](reports/hul-phase2-review.md) and [hindustan-unilever-limited-panel-coverage.md](reports/hindustan-unilever-limited-panel-coverage.md). The HUL PDF cache hash and ledger entries retain official source URL, page, snippet, reviewer, and status.

## Verification run

- Tests: **31 passed, 0 failed** (`python scripts/run_tests.py`).
- Dashboard: Streamlit app runner completed with **0 exceptions**; local health endpoint returned **HTTP 200 `ok`**. The `eval` import failure was fixed by adding the repository root to the app's import path.
- Synthetic evaluation: canary recall **100%** (20 planted cases), false-positive rate **5%** (1 of 20 clean cases), missing-data abstain correctness **100%** (4/4), determinism **100%**, window stability **72.5%**. These are synthetic measurements only.
- Evidence grounding: 61 of 61 checked output claims mapped to ledger evidence; 0 unsupported claims in that run.
- Real-company reconciliation: unavailable (0 published figures compared). Blind human baseline review: unavailable.

## Remaining before project completion

- Add additional reviewed peer-company histories with compatible scope, basis, currency, and periods. ITC currently has four historical periods in its comparable pre-demerger cohort; it alone cannot supply the required peer evidence.
- Obtain and review a six-period volume-growth series only if its definition and reporting perimeter match the revenue growth input. Current HUL disclosures use underlying growth measures with acquisition/disposal adjustments, so unreviewed figures must not be paired with reported revenue as if automatically comparable.
- Add independent, source-backed red-team evidence for seasonality, one-offs, accounting changes, acquisitions/demergers, pricing lags, and sector movements.
- Measure real-world reconciliation, blind human-baseline results, and longitudinal outcomes. Synthetic evaluation is not real-company validation.
- Improve filing discovery and automate extraction-to-source reconciliation. Extraction candidates remain unverified until a reviewer checks the original source.

There is no validated real-company discovery at this time. A finding requires the existing validation gate to pass with traceable evidence; thresholds remain unchanged.
