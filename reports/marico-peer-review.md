# Marico data review — initial consolidated batch

Review date: 2026-10-19. This is a two-period manually reviewed batch from Marico Limited's official Integrated Annual Report 2024–25. It is useful for testing the fourth-company ingestion and dossier path, but it is not a six-period peer panel and does not qualify as a compatible peer for HUL or ITC's standalone panels.

## Source and provenance

- Official report: [Marico Integrated Annual Report 2024–25](https://marico.com/investorspdf/Marico_Annual_Report_FY25.pdf)
- Cached PDF: `data/cache/74e0f6c239f6b611a1d66f361988a65f52bdfb51956ada929de3f4857b1e3474.pdf`
- SHA-256: `74e0f6c239f6b611a1d66f361988a65f52bdfb51956ada929de3f4857b1e3474`
- Reviewed PDF page: 170 (printed pages 336–337), which contains the Consolidated Balance Sheet and Consolidated Statement of Profit and Loss side by side.
- Reported unit: INR crore. Basis: consolidated. Fiscal periods: years ended/as at 31 March. Reviewer: Codex visual review, 2026-10-19.

The intake extractor proposed four unverified balance-sheet values and did not extract revenue. I checked the rendered original page manually, recorded the six observations below through the verified `record` path, and linked the four extraction proposals to the matching ledger entries. The candidate links do not write duplicate ledger rows.

## Verified observations

| Ledger ID | Metric | Exact value | Period | Source row and columns |
|---|---|---:|---|---|
| L0089 | Revenue from operations | 10,831 INR crore | FY2025 | Consolidated Statement of Profit and Loss, 31 March 2025 column |
| L0090 | Revenue from operations | 9,653 INR crore | FY2024 | Consolidated Statement of Profit and Loss, 31 March 2024 comparative column |
| L0091 | Inventory | 1,235 INR crore | FY2025 | Consolidated Balance Sheet, as at 31 March 2025 |
| L0092 | Inventory | 1,336 INR crore | FY2024 | Consolidated Balance Sheet, as at 31 March 2024 |
| L0093 | Trade receivables | 1,271 INR crore | FY2025 | Consolidated Balance Sheet, as at 31 March 2025 |
| L0094 | Trade receivables | 1,069 INR crore | FY2024 | Consolidated Balance Sheet, as at 31 March 2024 |

Each observation retains the official source URL, the cached SHA-256, PDF page, exact snippet, annual period dates, currency/unit, consolidated designation, reporting scope, cohort, reviewer, and verified status in `data/ledger.jsonl`.

## Analysis result and limits

Command: `python scripts/argus.py run --company "Marico Limited"`.

- Result: `no_reliable_finding`; six verified observations; one panel; zero generated candidates; zero rejected candidates.
- `receivable_days` and `inventory_days` calculate values for FY2024 and FY2025 but abstain because only 2 of the required 6 periods are available.
- `price_volume` abstains because matched revenue and disclosed volume-growth inputs are required.
- `cash_conversion` abstains because matched operating-cash-flow and EBITDA inputs are required.
- `margin_vs_input_cost` abstains because matched gross-margin and input-cost-index disclosures are required.
- No eligible peer panels were available for Marico's consolidated cohort. Its basis also differs from the three reviewed companies' standalone historical cohorts.

No finding is claimed. Extend this cohort only with manually checked consolidated data using periods and scope that remain comparable; do not fill the missing history with estimates or zeroes.

## Supplemental standalone peer panel

Review date: 2026-10-20. A separate standalone panel was added from manually checked annual-report statement pages. These rows are kept in a different cohort from the consolidated FY2024–25 rows above; the two bases are never combined.

| Fiscal year | Revenue (INR crore) | Inventory (INR crore) | Trade receivables (INR crore) | Official report / PDF page |
|---|---:|---:|---:|---|
| FY2020 | 5,853 | 1,165 | 465 | [FY2020–21](https://marico.com/investorspdf/annual-report-fy-2020-21.pdf), p.151, comparative columns marked “Recast” |
| FY2021 | 6,337 | 873 | 310 | [FY2020–21](https://marico.com/investorspdf/annual-report-fy-2020-21.pdf), p.151 |
| FY2022 | 7,500 | 1,093 | 555 | [FY2022–23](https://marico.com/investorspdf/Marico_Annual_Report_FY23.pdf), p.178 |
| FY2023 | 7,478 | 895 | 838 | [FY2022–23](https://marico.com/investorspdf/Marico_Annual_Report_FY23.pdf), p.178 |
| FY2024 | 7,002 | 936 | 870 | [FY2024–25](https://marico.com/investorspdf/Marico_Annual_Report_FY25.pdf), p.215 |
| FY2025 | 7,581 | 804 | 935 | [FY2024–25](https://marico.com/investorspdf/Marico_Annual_Report_FY25.pdf), p.215 |

All 18 observations are standalone, annual, INR crore, and company-total scope. Each row is manually checked against the rendered PDF statement table and stored with its exact official URL, cached-file SHA-256, PDF page, exact row snippet, date range, reviewer identity, and verified status in the append-only ledger. The cached hashes are:

- FY2020–21 report: `a84d5c622d999c796ab02c2000f8fe2025438602d4ce1bfb4a621a0fff304df0`
- FY2022–23 report: `0f41759d903f2f9e1185d1bd52228a1653592583ca729abe75edf430b9332b0a`
- FY2024–25 report: `74e0f6c239f6b611a1d66f361988a65f52bdfb51956ada929de3f4857b1e3474`

FY2020 is explicitly labeled “Recast” in the FY2020–21 standalone statement columns. That disclosure is retained in its row-level comparability note; no pre-FY2020 values are included. We have not inferred the reason for the recast from this page alone. The Marico panel is now six verified annual periods for revenue, inventory, and trade receivables. Volume-growth data remains unavailable in a matched six-period scope, so volume-sensitive metrics continue to abstain. The consolidated two-period cohort remains separate and is not eligible as a standalone peer panel.
