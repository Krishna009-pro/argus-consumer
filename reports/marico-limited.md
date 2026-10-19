# ARGUS-Consumer dossier — Marico Limited

## Discovery
No persistent, peer-adjusted anomaly cleared the deterministic screening criteria.

## Why it matters
- Reported values are compared with the company’s own historical range.
- The workflow separates calculated deviations from explanations and abstains when independent evidence is missing.

## Linked evidence
- L0089
- L0090
- L0091
- L0092
- L0093
- L0094

## Timeline
- {'period': 'FY2025', 'angle': 'price_volume', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0090', 'L0089'], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'receivable_days', 'reported': 42.83214846274582, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0093', 'L0089'], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'inventory_days', 'reported': 41.61896408457206, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0091', 'L0089'], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'cash_conversion', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': [], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'margin_vs_input_cost', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': [], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}

## Numerical evidence
- receivable_days FY2024 [L0094] [L0090]: 40.53185538174661
- receivable_days FY2025 [L0093] [L0089]: 42.83214846274582
- inventory_days FY2024 [L0092] [L0090]: 50.65534030871232
- inventory_days FY2025 [L0091] [L0089]: 41.61896408457206

## Counterargument
Seasonality, base effects, one-off events, accounting changes, acquisitions, pricing lags and sector movement remain alternatives unless independently tested.

## Falsification condition
The signal should be withdrawn if subsequent comparable periods return within the historical range or verified peer/source evidence explains the deviation.

## Evidence strength
Weak (score 0.0)

## Not tested
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — price_volume: Matched revenue and disclosed volume-growth inputs are required.
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — receivable_days: Fewer than six usable disclosed periods (2 of 2).
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — inventory_days: Fewer than six usable disclosed periods (2 of 2).
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — cash_conversion: Matched operating-cash-flow and EBITDA inputs are required.
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — margin_vs_input_cost: Matched gross-margin and input-cost-index disclosures are required.
- Peer-adjusted comparison: no eligible peer panels were available.

## Hypotheses (unverified)
- None; optional research model is not configured or no source excerpts were available.

## Red-team review
- Not run.
