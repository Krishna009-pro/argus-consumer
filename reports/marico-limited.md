# ARGUS-Consumer dossier — Marico Limited

## Discovery
A persistent historical-range deviation remains in receivable_days; it is unverified as a business explanation.

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
- L0095
- L0096
- L0097
- L0098
- L0099
- L0100
- L0101
- L0102
- L0103
- L0104
- L0105
- L0106
- L0107
- L0108
- L0109
- L0110
- L0111
- L0112

## Timeline
- {'period': 'FY2025', 'angle': 'price_volume', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0090', 'L0089'], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'receivable_days', 'reported': 42.83214846274582, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0093', 'L0089'], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'inventory_days', 'reported': 41.61896408457206, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0091', 'L0089'], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'cash_conversion', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': [], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'margin_vs_input_cost', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': [], 'status': 'abstained', 'consolidation_basis': 'consolidated', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_consolidated_FY2024_FY2025'}
- {'period': 'FY2025', 'angle': 'price_volume', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': ['L0099', 'L0100'], 'status': 'abstained', 'consolidation_basis': 'standalone', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_standalone_FY2020_FY2025_recast_FY2020'}
- {'period': 'FY2025', 'angle': 'receivable_days', 'reported': 45.017148133491624, 'expected_low': 11.406043780286257, 'expected_high': 44.68135242678704, 'ledger_ids': ['L0112', 'L0100'], 'status': 'tested', 'consolidation_basis': 'standalone', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_standalone_FY2020_FY2025_recast_FY2020'}
- {'period': 'FY2025', 'angle': 'inventory_days', 'reported': 38.70993272655323, 'expected_low': 37.64161175014271, 'expected_high': 65.83431197822506, 'ledger_ids': ['L0106', 'L0100'], 'status': 'tested', 'consolidation_basis': 'standalone', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_standalone_FY2020_FY2025_recast_FY2020'}
- {'period': 'FY2025', 'angle': 'cash_conversion', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': [], 'status': 'abstained', 'consolidation_basis': 'standalone', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_standalone_FY2020_FY2025_recast_FY2020'}
- {'period': 'FY2025', 'angle': 'margin_vs_input_cost', 'reported': None, 'expected_low': None, 'expected_high': None, 'ledger_ids': [], 'status': 'abstained', 'consolidation_basis': 'standalone', 'reporting_scope': 'company_total_operations', 'comparability_cohort': 'Marico_standalone_FY2020_FY2025_recast_FY2020'}

## Numerical evidence
- receivable_days FY2024 [L0094] [L0090]: 40.53185538174661
- receivable_days FY2025 [L0093] [L0089]: 42.83214846274582
- inventory_days FY2024 [L0092] [L0090]: 50.65534030871232
- inventory_days FY2025 [L0091] [L0089]: 41.61896408457206
- receivable_days FY2020 [L0107] [L0095]: 29.077396207073296
- receivable_days FY2021 [L0108] [L0096]: 17.855452106675084
- receivable_days FY2022 [L0109] [L0097]: 27.009999999999998
- receivable_days FY2023 [L0110] [L0098]: 40.90264776678256
- receivable_days FY2024 [L0111] [L0099]: 45.47557840616967
- receivable_days FY2025 [L0112] [L0100]: 45.017148133491624
- inventory_days FY2020 [L0101] [L0095]: 72.84982060481804
- inventory_days FY2021 [L0102] [L0096]: 50.28325706170112
- inventory_days FY2022 [L0103] [L0097]: 53.19266666666666
- inventory_days FY2023 [L0104] [L0098]: 43.68480877239904
- inventory_days FY2024 [L0105] [L0099]: 48.92544987146529
- inventory_days FY2025 [L0106] [L0100]: 38.70993272655323

## Counterargument
Seasonality, base effects, one-off events, accounting changes, acquisitions, pricing lags and sector movement remain alternatives unless independently tested.

## Falsification condition
The signal should be withdrawn if subsequent comparable periods return within the historical range or verified peer/source evidence explains the deviation.

## Evidence strength
Weak (score 59.44)

## Not tested
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — price_volume: Matched revenue and disclosed volume-growth inputs are required.
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — receivable_days: Fewer than six usable disclosed periods (2 of 2).
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — inventory_days: Fewer than six usable disclosed periods (2 of 2).
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — cash_conversion: Matched operating-cash-flow and EBITDA inputs are required.
- consolidated, company_total_operations, Marico_consolidated_FY2024_FY2025 — margin_vs_input_cost: Matched gross-margin and input-cost-index disclosures are required.
- standalone, company_total_operations, Marico_standalone_FY2020_FY2025_recast_FY2020 — price_volume: Matched revenue and disclosed volume-growth inputs are required.
- standalone, company_total_operations, Marico_standalone_FY2020_FY2025_recast_FY2020 — cash_conversion: Matched operating-cash-flow and EBITDA inputs are required.
- standalone, company_total_operations, Marico_standalone_FY2020_FY2025_recast_FY2020 — margin_vs_input_cost: Matched gross-margin and input-cost-index disclosures are required.

## Hypotheses (unverified)
- None; optional research model is not configured or no source excerpts were available.

## Red-team review
- seasonality: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
- base_effect: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
- one_off_event: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
- accounting_change: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
- acquisition: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
- pricing_lag: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
- sector_trend: not_tested — No reviewed source with a valid cached hash, locator, and exact snippet was supplied.
