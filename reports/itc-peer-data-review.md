# ITC peer data review — FY2024 addition and date alignment

Review date: 2026-10-19. This review covers source-checked FY2024 observations and correction of fiscal-date metadata for the earlier ITC standalone series. It does not alter engine logic or configured thresholds.

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

The verified pre-demerger standalone panel now contains seven consecutive periods, FY2018–FY2024, with revenue, inventory, and trade receivables. Source statements confirm the annual periods: ITC Report and Accounts 2021 PDF pp.178–179 explicitly label values as at/for the years ended 31 March 2021 and 31 March 2020; the 2023 report PDF pp.184–185 labels 31 March 2023 and 31 March 2022. Ledger date metadata on L0045–L0056 was corrected to those source periods. This correction changed dates only; it did not change any financial value, unit, scope, basis, source URL, or hash. `tests/test_historical_period_metadata.py` locks the reviewed period mapping.

The seven-period series is sufficient for the engine to test receivables-days and inventory-days. In the current regenerated analysis, each angle has one outside-range period (FY2023); neither reaches the unchanged three-consecutive-period persistence rule. The engine reports `no_reliable_finding`, with zero generated candidates and zero rejected candidates. HUL and Britannia are compatible peer panels. Britannia now has six verified periods and both derived angles are tested, but it has no flagged periods; there are still only two distinct compatible peers for ITC and the configured three-peer baseline is unmet. See [britannia-peer-review.md](britannia-peer-review.md) for the full manually reviewed batch.

ITC's FY2025 annual report separates Hotels discontinued operations from continuing operations, and the Hotels series shown there covers only nine months through 31 December 2024. Post-demerger balance sheets also have a changed perimeter. These rows remain isolated in their existing scopes/cohorts; they are not appended to the full-operations pre-demerger history. Do not combine them unless the issuer publishes an explicitly comparable series and the ledger records that scope.

## Analysis and abstentions

Latest command: `python scripts/argus.py run --company "ITC Limited"`.

- Generated result: `no_reliable_finding`; 38 evidence entries used in the dossier; 12 panels; 0 generated candidates; 0 rejected candidates.
- Main seven-period panel: `receivable_days` and `inventory_days` are tested. Each has a gap flag only for FY2023; neither is persistent for three consecutive periods. Supporting inputs are L0045–L0056 and L0062–L0070.
- Main-panel `price_volume` abstains because matched revenue and disclosed volume growth are required; `cash_conversion` needs matched operating cash flow and EBITDA; `margin_vs_input_cost` needs matched gross-margin and input-cost-index disclosures. These input series are absent; the seven annual revenue/inventory/receivable observations do not substitute for them.
- The FY2024-only balance-sheet cohort abstains on `inventory_days` with `Inventory, a same-unit positive denominator, and exact period day count are required.` It remains isolated and is not merged with the historical cohort.
- Compatible peer panels: Hindustan Unilever Limited and Britannia Industries Limited. Britannia's six-period standalone receivables-days and inventory-days angles are tested with no flagged periods. ITC still has only two distinct compatible peer companies; the three-peer adjusted check cannot run. Other ITC cohorts remain isolated when their basis or reporting scope differs, including post-Hotels-demerger continuing operations.
- No real discovery is claimed. Period alignment is corrected; peer breadth and multiple other data inputs remain insufficient.
