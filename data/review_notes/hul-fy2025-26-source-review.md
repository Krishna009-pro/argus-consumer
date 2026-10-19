# HUL FY 2025–26 source review

Review date: 2026-10-18  
Company: Hindustan Unilever Limited  
Source: [official HUL Integrated Annual Report 2025–26](https://www.hul.co.in/files/annual-report-2025-26.pdf)  
Local source: `data/incoming/hul-annual-report-2025-26.pdf`  
Cached source: `data/cache/98219f80b28472d4d11c893274e0537b5098c98f34dcc30c7f905db3cb7a929b.pdf`  
SHA-256: `98219f80b28472d4d11c893274e0537b5098c98f34dcc30c7f905db3cb7a929b`

The original statement pages were rendered and visually checked against the row labels, year headings, units and standalone/consolidated headings. Values below are manually transcribed from those pages and recorded as verified ledger entries. “PDF page” is the physical page index; “printed page” is the report footer number.

## Verified observations

All amounts are INR crore. Income statement values are for continuing operations. Balance sheet values are as at the stated date.

| Metric | FY2025 | FY2026 | Basis | PDF page (printed page) | Ledger IDs FY2025 / FY2026 | Scope / comparability |
|---|---:|---:|---|---|---|---|
| Revenue from operations | 59,676 | 61,975 | Standalone | 139 (275) | L0002 / L0001 | Continuing operations; report’s two-year comparative |
| Revenue from operations | 61,328 | 64,468 | Consolidated | 184 (365) | L0004 / L0003 | Continuing operations; report’s two-year comparative |
| Inventories, as at 31 March | 4,161 | 4,383 | Standalone | 138 (273) | L0007 / L0005 | FY2025 pre-demerger; FY2026 post-demerger; separate cohorts |
| Trade receivables, as at 31 March | 3,450 | 3,037 | Standalone | 138 (273) | L0008 / L0006 | FY2025 pre-demerger; FY2026 post-demerger; separate cohorts |
| Inventories, as at 31 March | 4,415 | 4,789 | Consolidated | 183 (363) | L0011 / L0009 | FY2025 pre-demerger; FY2026 post-demerger; separate cohorts |
| Trade receivables, as at 31 March | 3,819 | 3,379 | Consolidated | 183 (363) | L0012 / L0010 | FY2025 pre-demerger; FY2026 post-demerger; separate cohorts |

Each row above represents two ledger observations, one for each year: 12 observations total. Each ledger row retains the official URL, cache path and SHA-256, physical PDF page, exact source snippet, period, unit, currency, basis, review status and comparability tags. Reviewer field identifies this run’s visual source-page review; it does not claim that a human user personally approved the entries.

## Discontinued operations and limitations

- The P&L statements on PDF pages 139 and 184 distinguish continuing operations from discontinued operations. The FY2025 revenue comparatives recorded here are the figures shown under continuing operations, not total revenue including discontinued operations.
- The consolidated notes on PDF page 224 (printed page 444) separately show the discontinued undertaking’s financial position as at 30 November 2025, including inventory INR 204 crore, trade receivables INR 44 crore, total assets INR 1,404 crore, liabilities INR 528 crore and net assets transferred INR 876 crore. Those one-off transfer-date values are context, not annual observations for the ARGUS panel.
- The report’s ratio note on PDF page 48 (printed page 92) says FY2026 ratios are based on continuing operations following the Ice Cream business demerger and FY2025 ratios are not strictly comparable. We therefore do not use those ratios as a continuous historical series.
- Balance sheet FY2025 closing values predate the demerger; FY2026 closing values follow it. They are preserved but split into separate comparability cohorts. No working-capital trend is inferred across this scope break.
- No previous annual report was locally available and independently page-checked for this run. No older years were added from external recollection or unverified extraction.

## Extraction review status

Import created 56 unverified machine candidates. Six candidates that captured note references (11, 12, 25 or 27) instead of table values were marked rejected in the candidate manifest. The remaining 50 candidates stay unverified; they were not admitted to analysis. Twelve verified observations were entered from the visually checked source rows, including corrected values where extraction did not produce the right number. Missing or ambiguous claims were not changed to zero.

## Reproduction

```powershell
python scripts/argus.py import-local .\data\incoming\hul-annual-report-2025-26.pdf --company "Hindustan Unilever Limited" --source-url https://www.hul.co.in/files/annual-report-2025-26.pdf
python scripts/argus.py run --company "Hindustan Unilever Limited"
```

