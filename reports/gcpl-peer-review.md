# Godrej Consumer Products Limited peer data review

## Review outcome

This review adds 18 manually checked standalone observations from official GCPL reports: revenue from operations, inventories, and trade receivables for FY2020–FY2025. Every ledger row is linked to the cached PDF, its SHA-256, exact PDF page, source URL, table text, reviewer, period, unit, currency, and basis. The source pages were rendered and checked against the original PDFs before approval.

| Fiscal year | Revenue from operations (INR crore) | Inventory (INR crore) | Trade receivables (INR crore) | Statement pages |
|---|---:|---:|---:|---|
| FY2020 | 5,474.45 | 657.72 | 305.52 | FY2020–21 report, PDF pp. 283–284 (printed pp. 280–281) |
| FY2021 | 6,254.33 | 702.83 | 247.46 | FY2020–21 report, PDF pp. 283–284 (printed pp. 280–281) |
| FY2022 | 6,951.56 | 790.84 | 336.92 | FY2021–22 report, PDF pp. 294–295 (printed pp. 292–293) |
| FY2023 | 7,667.17 | 591.60 | 320.79 | FY2022–23 audited exchange filing, PDF pp. 2 and 4 |
| FY2024 | 8,411.40 | 646.86 | 491.34 | FY2024–25 report, PDF pp. 402–403 (printed pp. 400–401) |
| FY2025 | 8,910.15 | 697.14 | 595.62 | FY2024–25 report, PDF pp. 402–403 (printed pp. 400–401) |

The values and their ledger IDs are in `data/ledger.jsonl`: FY2020 L0131–L0133, FY2021 L0134–L0136, FY2022 L0137–L0139, FY2023 L0140–L0142, FY2024 L0143–L0145, and FY2025 L0146–L0148. PDF page numbers above are physical page numbers. FY2020 is a comparative column in the FY2020–21 report; FY2021 is the current column there. FY2022 is the current year in the FY2021–22 report. FY2023 comes from the standalone columns of the audited annual results filed with NSE. FY2024 is the comparative column in the FY2024–25 report, and FY2025 is its current year.

## Cached source files and hashes

| Source | Official URL | Cached file SHA-256 |
|---|---|---|
| FY2020–21 annual report | [Godrej Consumer Products annual report](https://www.godrejcp.com/uploads/GCPL_Annual_Report_202021_compressed_ac4fbb1eb2.pdf) | `67db090f2fe17b1d2ab40875309cdefaf8d889264e55b109f91cc3da2d3add55` |
| FY2021–22 annual report | [Godrej Consumer Products annual report](https://www.godrejcp.com/uploads/GCPL_Annual_Report_202122_compressed_0ef87ff8a7.pdf) | `906f24cf5e49a2a0d85eecceeb16da77eefabcdd181c2a64a1912050f9a7e681` |
| FY2022–23 audited annual results | [NSE filing](https://nsearchives.nseindia.com/corporate/GODREJCP_10052023160114_GCPL_FR_signed.pdf) | `b78e63fb125d6ac72010b2fefbb34400ed3d2042cf996ab5d0e417c31b22d2a2` |
| FY2024–25 annual and integrated report | [Godrej Consumer Products annual report](https://www.godrejcp.com/uploads/GCPL_Annual_and_Integrated_Report_2024_25_1_a988ff386b.pdf) | `70b1e1c718091f8be4ad084c637938fe7d89356e847e55021217819b0a939dfa` |

The FY2024–25 standalone report states that GCPL acquired the Raymond Consumer Care FMCG business on 8 May 2023. It reports ₹466 crore of acquired-business product sales for the eleven months through 31 March 2024 and says the business was integrated with GCPL. This is a material perimeter break for standalone history. To avoid treating pre- and post-acquisition observations as one continuous baseline, FY2020–FY2023 and FY2024–FY2025 are stored as separate comparability cohorts. The source describes the acquisition in PDF p. 476 (printed p. 474). Consolidated results are excluded from this standalone panel. The FY2023 standalone exchange filing says the statements include one Singapore branch; no branch-only adjustment is disclosed in this series. No discontinued-operation values were imputed or added.

## Analysis output

Command: `python scripts/argus.py run --company "Godrej Consumer Products Limited"`

Result: `no_reliable_finding`; 18 verified observations; two isolated comparability panels; zero generated candidates; zero rejected candidates.

- **Pre-acquisition cohort (FY2020–FY2023):** receivable-days and inventory-days are calculated, but each abstains because four periods are below the six-period minimum. The reported series are 20.43, 14.44, 17.69, and 15.27 receivable-days; and 43.97, 41.02, 41.52, and 28.16 inventory-days.
- **Post-acquisition cohort (FY2024–FY2025):** receivable-days are 21.38 and 24.40; inventory-days are 28.15 and 28.56. Both angles abstain because only two comparable periods are available.
- **Price/volume:** abstained; there is no verified revenue-matched volume-growth series.
- **Cash conversion:** abstained; matched operating cash flow and EBITDA inputs are absent.
- **Margin versus input cost:** abstained; matched gross-margin and input-cost-index data are absent.

No finding is presented as a discovery. The existing thresholds and validation gates were not changed.

## M01 published-figure reconciliation

The report publishes standalone debtor-turnover values of **20.36 (FY2024)** and **16.22 (FY2025)**, and inventory-turnover values of **13.35 (FY2024)** and **13.12 (FY2025)** on PDF p. 90 (printed p. 88). Its formula note is on PDF p. 91 (printed p. 89): debtor turnover is net sales divided by average opening and closing trade receivables; inventory turnover is net sales divided by average opening and closing inventories.

All four figures and formula snippets are visually verified and recorded in `data/reconciliation/published_figures.json` with their source URL, SHA-256, page, extraction status, review status, and reviewer. They are **excluded** from the M01 denominator because ARGUS currently computes receivable-days as closing receivables divided by revenue from operations times period days, and inventory-days as closing inventory divided by revenue from operations times period days. The published formulas use average balances and produce turnover multiples. Thus the current real-company M01 result is **0 matched / 0 compared; four verified references excluded for formula mismatch; unavailable**. The data set makes these exclusions explicit rather than converting unlike measures or claiming a reconciliation.

## Remaining GCPL coverage gaps

- The acquisition split leaves only four pre-acquisition periods and two post-acquisition periods, so neither cohort clears the six-period analysis minimum.
- No comparable volume, operating cash-flow/EBITDA pair, or input-cost index has been added.
- GCPL's turnover ratios do not reconcile to the current ARGUS days formulas. A future reconciliation must use a published figure with an identical formula, period, denominator, basis, and scope or leave that comparison excluded.
