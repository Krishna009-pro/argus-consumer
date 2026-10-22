# M01 formula discovery log

**Reviewed:** 2026-10-21
**Purpose:** Find published definitions that exactly match the existing ARGUS days calculations, without changing formulas or thresholds.

## Search method

The configured OpenRouter LLM was used as a source-finding assistant over extracted text from cached public reports. A first request containing 100 page excerpts closed with an incomplete response; none of that response was used. A smaller request with eight targeted pages completed and returned no exact matches. The model's output was treated only as a search aid. Formula eligibility below is based on direct report text and page review.

## Findings in the current FMCG company set

| Company and period | Report evidence | M01 decision |
|---|---|---|
| HUL, FY2025–26 | Official annual report, cached SHA-256 `98219f80b28472d4d11c893274e0537b5098c98f34dcc30c7f905db3cb7a929b`, PDF p. 175. The report defines inventory turnover as sales divided by average inventory and trade receivables turnover as sales divided by average accounts receivables. | Exclude: average balances and turnover multiples; neither is the required closing-balance days formula. |
| ITC, FY2024–25 | Official annual report, cached SHA-256 `2a51bc137e460a2549785e784465e6fe1aa7bcd2ca1077d6e2d2465efdd27acc`, PDF p. 214. The ratio table uses gross revenue from sales of products and services over average inventory and average trade receivables. | Exclude: average balances, a different sales denominator, and turnover multiples. |
| Dabur, FY2024–25 and FY2023–24 | Official annual report, cached SHA-256 `3767d5d09cc94e453543a4f4333187fd317ab03ac40e2122ee937436e4e85ae3`, PDF p. 151 (printed p. 148). The “Working Capital (No. of days of sales)” table reports inventories 66.8/57.3 days and receivables 25.8/27.5 days. It does not state the calculation formula or clearly label the table's consolidation basis. The report separately defines turnover ratios using average receivables and average inventory on PDF p. 331. | Keep unresolved; do not match values by guessing the formula or basis. |
| GCPL, FY2024–25 and FY2023–24 | The four published turnover figures and their formulas are already visually reviewed and traceable in `config/reconciliation.yaml`; the formulas use net sales and average balances. | Excluded by the evaluator for formula mismatch. |

The Dabur report is available at the [official annual-report PDF](https://www.dabur.com/digital-annual-reports/reports/dabur-india-annual-report-2024-25.pdf). The values above remain report observations only; they were not promoted into the verified M01 reference set because the formula and basis are unresolved.

## External leads that do not qualify as FMCG peer references

Search-result text surfaced apparent closing-balance/revenue-from-operations day formulas in some official offer documents. For example, the [Advanta Enterprises DRHP filed with SEBI](https://www.sebi.gov.in/filings/public-issues/jan-2026/advanta-enterprises-limited-drhp_99228.html) links to a [company DRHP](https://www.goldmansachs.com/worldwide/india/ipo/advanta-enterprises-limited/DRHP.pdf) whose indexed text appears to define receivable-days and inventory-days with closing balances. Advanta is an agricultural seed business, not a comparable FMCG peer. Its offer document has not been imported, cached, or manually reviewed in this project, so these search leads contribute no M01 entry. Other search leads use average balances, COGS, or short-period day counts and are also ineligible for the current comparison.

## Result

No new reference was added. `python scripts/argus.py eval` remains **M01 unavailable: 0 matched / 0 compared; 4 verified GCPL references excluded for formula mismatch**. The next useful search should target FMCG issuers whose audited reports explicitly define closing inventory or receivables divided by revenue from operations, with the same fiscal period, basis, and scope as the ledger inputs.
