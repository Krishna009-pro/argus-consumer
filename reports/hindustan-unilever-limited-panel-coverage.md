# HUL panel coverage and engine result

Run date: 2026-10-19  
Engine status: `no_reliable_finding`  
Verified ledger rows: 30  
Panels: 7  
Generated finding candidates: 0  
Rejected finding candidates: 0

## Panel inventory

| Basis | Scope | Cohort | Periods | Coverage |
|---|---|---|---|---|
| Standalone | Continuing operations | FY2025–26 report comparatives | FY2025–FY2026 | Revenue only; 2 years |
| Consolidated | Continuing operations | FY2025–26 report comparatives | FY2025–FY2026 | Revenue only; 2 years |
| Standalone | Total balance sheet | Pre-demerger FY2025 | FY2025 | Inventory and receivables; 1 year |
| Standalone | Total balance sheet | Post-demerger FY2026 | FY2026 | Inventory and receivables; 1 year |
| Consolidated | Total balance sheet | Pre-demerger FY2025 | FY2025 | Inventory and receivables; 1 year |
| Consolidated | Total balance sheet | Post-demerger FY2026 | FY2026 | Inventory and receivables; 1 year |
| Standalone | Total operations, pre-demerger | FY2020–FY2025 historical cohort | FY2020–FY2025 | Revenue, inventory and receivables; 6 years each |

## Historical panel observations and screen

The verified standalone pre-demerger panel contains revenue, inventory, and trade receivables for all six fiscal years FY2020–FY2025. All figures are INR crore; source pages and ledger IDs are in [the detailed review](hul-phase2-review.md).

Receivables days are 9.8707, 13.0777, 13.7749, 16.8787, 16.2817, and 20.4859. FY2025 is above the calculated historical expected band of 7.7908–19.0617. The unchanged persistence gate requires at least three consecutive flagged periods; only FY2025 is flagged, so the engine generates no candidate.

Revenue-based inventory days are 24.8750, 26.8457, 27.7352, 24.8768, 23.0728, and 24.7078. FY2025 is within the expected band of 22.9395–28.7831. This uses revenue as denominator because a comparable verified cost-of-goods-sold series is unavailable; it is not cost-of-sales inventory turnover.

## Coverage gaps and abstentions

- Continuing-operations revenue panels have two comparable years each, four fewer than the six-period minimum. Historical balance-sheet cohorts remain separate because the Ice Cream business is reported as discontinued operations and the demerger changes scope.
- Six short panels abstain on all five angles. For `price_volume`, `receivable_days`, `cash_conversion`, and `margin_vs_input_cost`, the exact reason is `Fewer than six usable disclosed periods.` For `inventory_days`, it is `Inventory, a same-unit positive denominator, and exact period day count are required.`
- In the six-year historical panel, `price_volume`, `cash_conversion`, and `margin_vs_input_cost` each abstain with `Fewer than six usable disclosed periods.` No verified volume-growth series, matched operating-cash-flow/EBITDA pair, or gross-margin/input-cost-index pair is available.
- Historical `receivable_days` and `inventory_days` are tested. Receivables have one flagged period but no candidate. Inventory has no flagged period.
- There is no eligible peer panel. Red-team alternatives are recorded as not tested because independently retrieved, cached evidence was not available.
- The peer-adjusted deviation function requires three peer-gap observations and counts each peer company once; a single ITC panel cannot meet that gate. Comparable scope and basis must also be established before peer rows are eligible.
- No six-period volume-growth series with scope compatible with the full standalone revenue panel is present, so `price_volume` abstains.
- No missing observation is filled with zero. The six-year historical panel is standalone only; comparable six-year consolidated observations and peer observations are absent.

## Verification and artifacts

- Test suite: 27 passed, 0 failed.
- Synthetic evaluation: measured separately from real-company quality. The HUL result remains an abstention/no-reliable-finding.
- Dashboard health: `http://127.0.0.1:8765/_stcore/health` returned HTTP 200 `ok`.
- Current dossier: `reports/hindustan-unilever-limited.md`; machine-readable panel analysis: `reports/hindustan-unilever-limited-analysis.json`; exported PDF: `reports/hindustan-unilever-limited.pdf`.
- No threshold change and no HUL-specific engine code.

