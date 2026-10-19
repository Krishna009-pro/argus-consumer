# Britannia peer-data review — six-year verified batch

Review date: 2026-10-19. This review records the six-period, standalone historical panel manually transcribed from Britannia Industries Limited's official annual reports. It does not alter engine logic or thresholds.

## Sources and review method

| Fiscal coverage | Official source | Cached PDF SHA-256 | Evidence pages (one-based PDF page) |
|---|---|---|---|
| FY2024–FY2025 | [Annual Report 2024–25](https://media.britannia.co.in/B_Il_Annual_Report_for_FY_2024_25_b6d95d1717.pdf) | `7beb4f068f51ee4e4efca4b6146355faa8ad66eef49973a920f2649e387a5f80` | Revenue p.106; standalone balance sheet p.89 |
| FY2022–FY2023 | [Annual Report 2022–23](https://media.britannia.co.in/Annual_Report_2022_23_988ac4516b.pdf) | `f8a1ed521b658b24eecdcc897ceef7127508b525a73c5875eb673c38c40f2ddc` | Revenue p.89; standalone balance sheet p.73 |
| FY2020–FY2021 | [Annual Report 2020–21](https://media.britannia.co.in/Annual_Report_2020_21_be3a70d511.pdf) | `ecfb2308f3ef45a922be7e2cbca3eca67ada6ed6d24af75d82bd58d749599ab7` | Standalone P&L p.99; standalone balance sheet p.98 |

The PDFs were fetched through the existing public-source intake and SHA-256 cached. The regular extractor returned no candidate for the latest report. Earlier reports produced unverified proposals, which were not treated as evidence. Each ledger value below was manually checked against the rendered original PDF page, table heading/row, fiscal-year columns, units and standalone designation. Reviewer: Codex visual review, 2026-10-19. All values are INR crore. Periods are annual fiscal years ending 31 March; balance-sheet values are as at that date.

## Verified observations

| Period | Revenue from operations | Inventory | Trade receivables |
|---|---|---|---|
| FY2020 | 10,986.68 — L0084, PDF p.99 | 633.53 — L0086, PDF p.98 | 242.23 — L0088, PDF p.98 |
| FY2021 | 12,378.83 — L0083, PDF p.99 | 991.28 — L0085, PDF p.98 | 198.36 — L0087, PDF p.98 |
| FY2022 | 13,371.62 — L0078, PDF p.89 | 1,251.64 — L0080, PDF p.73 | 253.85 — L0082, PDF p.73 |
| FY2023 | 15,618.42 — L0077, PDF p.89 | 1,074.62 — L0079, PDF p.73 | 278.42 — L0081, PDF p.73 |
| FY2024 | 16,186.08 — L0072, PDF p.106 | 1,075.44 — L0074, PDF p.89 | 347.05 — L0076, PDF p.89 |
| FY2025 | 17,295.92 — L0071, PDF p.106 | 1,128.90 — L0073, PDF p.89 | 379.63 — L0075, PDF p.89 |

All 18 ledger rows retain source URL, cached file hash, PDF page, period dates, unit, standalone basis, `company_total_operations` scope, common six-year comparability cohort, reviewer and verified status. Cached files are under `data/cache/` using the recorded hashes. The full cohort is `Britannia_standalone_FY2020_FY2025`.

## Panel and current analysis

Command: `python scripts/argus.py run --company "Britannia Industries Limited"`.

- Result: `no_reliable_finding`; 18 verified entries; one panel; zero generated candidates; zero rejected candidates.
- The panel contains six annual periods (FY2020–FY2025) for revenue, inventory and trade receivables. `receivable_days` and `inventory_days` are tested. Neither has a gap flag in any of the six periods.
- `price_volume` abstains: `Matched revenue and disclosed volume-growth inputs are required.`
- `cash_conversion` abstains: `Matched operating-cash-flow and EBITDA inputs are required.`
- `margin_vs_input_cost` abstains: `Matched gross-margin and input-cost-index disclosures are required.`
- HUL and ITC are listed as compatible peer panels, but their full-company standalone histories do not provide three independent tested peer companies for a peer-adjusted check. A fourth company dossier and broader compatible panel coverage remain necessary for the configured company breadth and peer gates.

No anomaly, discovery or peer-adjusted conclusion is claimed. Inventory days here uses revenue as the denominator per the engine's available inputs; it is not cost-of-sales inventory turnover. Missing volume, cash-flow/EBITDA and margin/input-cost data remain absent rather than being filled with zero.
