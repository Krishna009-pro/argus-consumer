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
