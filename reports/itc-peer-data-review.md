# ITC peer data review — FY2024 addition

Review date: 2026-10-19. This review adds source-checked FY2024 observations to the general evidence ledger; it does not alter engine logic or configured thresholds.

## Source and verification

- Issuer: ITC Limited, Report and Accounts 2024 (official company PDF).
- Source URL: https://itcportal.com/content/dam/itc-corporate/pdfs/report-and-accounts/ITC-Report-and-Accounts-2024.pdf
- Cached file: `data/cache/6d1431d3947772ef2cbef9121b897ad985d3870e355618f530c7584a7d7f0f66.pdf`
- SHA-256: `6d1431d3947772ef2cbef9121b897ad985d3870e355618f530c7584a7d7f0f66`
- Basis: standalone; currency/unit: INR crore.
- Period: FY2024, year ended 31 March 2024 (balance-sheet values are as at 31 March 2024).
- Review: exact values and rows were checked against rendered PDF pages, in addition to cached text snippets. The PDF viewer page numbers below are one-based; printed report page numbers are shown separately.

| Ledger ID | Observation | Exact value | Source location | Exact cached snippet |
|---|---|---:|---|---|
| L0062 | Revenue from operations, annual FY2024 | 70,105.29 INR crore | PDF p.199; printed p.165; standalone Statement of Profit and Loss | `I Revenue From Operations 21A, 21B  70105.29  70251.28` |
| L0063 | Inventory, as at 31 March 2024 | 12,631.51 INR crore | PDF p.198; printed p.164; standalone Balance Sheet | `(a) Inventories 8 12631.51 10593.90` |
| L0064 | Trade receivables, as at 31 March 2024 | 3,311.45 INR crore | PDF p.198; printed p.164; standalone Balance Sheet | `(ii) Trade receivables 10  3311.45  2321.33` |

The entries are marked verified with reviewer `Codex visual review` and retain the source URL, SHA-256, cache path, page, snippet, basis, scope, and cohort in `data/ledger.jsonl`. The scope is full standalone operations before the Hotels demerger (`total_operations_pre_demerger`); it is not mixed with the continuing-only or discontinued-Hotels rows from the later report.

## Panel coverage and comparability

The current engine output contains one five-label pre-demerger standalone series (FY2020–FY2024 as labeled in the ledger) with revenue, inventory, and trade receivables. The existing six-period minimum is not met. The detector therefore has no tested ITC angle or candidate from this five-period panel. In the latest generated ITC dossier the company-level result is `no_reliable_finding`, with 0 generated candidates and 0 rejected candidates.

There is a data-contract issue that prevents treating the history as fully comparable to HUL yet: the existing ITC ledger rows L0045–L0056 have financial-year labels and `period_start`/`period_end` metadata that do not consistently agree. In particular, encoded annual date spans overlap FY2023 and FY2024. These rows were already present before this review. They have not been silently rewritten; the five-period count is the current engine's label-based panel, not confirmation that all dates are correctly aligned. Resolve the historical date metadata against each source report before using ITC as a period-aligned peer. This does not affect the manually verified values and source locations above, but it limits the peer claim.

ITC's FY2025 annual report separates Hotels discontinued operations from continuing operations, and the Hotels series shown there covers only nine months through 31 December 2024. Post-demerger balance sheets also have a changed perimeter. These rows remain isolated in their existing scopes/cohorts; they are not appended to the full-operations pre-demerger history. Do not combine them unless the issuer publishes an explicitly comparable series and the ledger records that scope.

## Analysis and abstentions

Latest command: `python scripts/argus.py run --company "ITC Limited"`.

- Generated result: `no_reliable_finding`; 32 verified entries reported by the CLI; 13 panels; 0 generated candidates; 0 rejected candidates.
- Main five-period panel: `price_volume`, `receivable_days`, `cash_conversion`, and `margin_vs_input_cost` abstain with `Fewer than six usable disclosed periods.`
- `inventory_days` abstains with `Inventory, a same-unit positive denominator, and exact period day count are required.` The displayed ratio series is exploratory output within an abstained angle and is not a tested finding.
- Other ITC panels are single-period or two-period scope/basis cohorts and abstain rather than being merged.
- No real discovery is claimed. Peer history is still insufficient and its historical period metadata needs review.
