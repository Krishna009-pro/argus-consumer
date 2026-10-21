# Dabur India Limited: standalone peer data review

## Review result

Eighteen observations were manually checked against rendered pages of Dabur's official annual reports and added to the verified evidence ledger. They form one annual, standalone panel for FY2020–FY2025: revenue from operations, closing inventories, and closing trade receivables. Amounts are INR crore. The panel is comparable by legal-entity reporting basis and annual period; it is not mixed with consolidated group values.

## Verified historical panel

| Fiscal year | Revenue from operations (INR crore) | Inventory (INR crore) | Trade receivables (INR crore) | Ledger IDs (revenue / inventory / receivables) |
|---|---:|---:|---:|---|
| FY2020 | 6,309.80 | 809.14 | 379.63 | L0128 / L0129 / L0130 |
| FY2021 | 7,184.73 | 1,114.16 | 281.24 | L0125 / L0126 / L0127 |
| FY2022 | 8,179.50 | 1,237.96 | 454.55 | L0122 / L0123 / L0124 |
| FY2023 | 8,684.35 | 1,223.77 | 561.18 | L0119 / L0120 / L0121 |
| FY2024 | 9,135.60 | 1,149.88 | 719.21 | L0116 / L0117 / L0118 |
| FY2025 | 9,070.71 | 1,288.07 | 600.58 | L0113 / L0114 / L0115 |

Revenue is the audited statement line “Revenue from operations.” Inventory and receivables are the year-end “Inventories” and “Trade receivables” balances. The FY2020, FY2022, and FY2024 values are comparative-column figures exactly as printed in the named reports; no interpolation or zero fill was used.

## Source and page provenance

| Report | Official source | Cached SHA-256 | PDF pages reviewed | Printed page numbers |
|---|---|---|---|---|
| FY2020–21 Annual Report | [Dabur official report](https://www.dabur.com/sites/default/files/2022-10/142394-Dabur-IR-2020-211.pdf) | `8de388f341ad66ef2e5024ff7804e0cb5b720e175e82e8c9c7665e93188d614d` | 228 (balance sheet), 229 (profit and loss) | 226–227 |
| FY2022–23 Integrated Annual Report | [Dabur official report](https://www.dabur.com/sites/default/files/2023-07/Annual%20Report%20%28including%20AGM%20Notice%29%20and%20BRSR%202022-23%20%281%29.pdf) | `5f12790ac539fe3d1f2795d6af7c617464030284f1b79b84158287149d450b9a` | 273 (balance sheet), 274 (profit and loss) | 270–271 |
| FY2024–25 Integrated Annual Report | [Dabur official report](https://www.dabur.com/Investors/Financial%20Information/Reports/Annual%20Reports/2024-25/Dabur%20India%20Limited%20Annual%20Report%202024-25.pdf) | `a2769cc905ca9c2a3b4a7b84ecef5aec0b449d9d32b4927306ad82159202355f` | 252 (balance sheet), 253 (profit and loss) | 250–251 |

Each row in `data/ledger.jsonl` stores the individual official URL, cache path, matching SHA-256, PDF page, exact table-row snippet, annual period dates, standalone basis, review status, and reviewer (`Codex visual review`). The source pages were rendered and the statement titles, year columns, units, and values were checked before the rows were recorded.

## Scope and comparability limits

- The series uses standalone statements consistently. Do not compare these values with Dabur consolidated panels or treat them as including subsidiaries.
- The FY2022–23 report states that Dabur completed acquisition of 51% of Badshah Masala on 2 January 2023 (PDF p.342; printed p.339). This changes the group consolidation perimeter from that date, but the acquired subsidiary is excluded from the standalone figures in this panel. The acquisition is retained here as a scope note, not used to adjust any number.
- The reviewed standalone income statements show “Revenue from operations” and do not provide a volume-growth series with a matching six-year definition and perimeter. Therefore price/volume analysis remains abstained.
- The reviewed statements show no separate discontinued-operations line in the selected financial statement pages. No discontinued-operation adjustment was made; a separate value is not inferred.
- A printed “-” or a missing disclosure was not converted into zero. No missing fields were needed for this three-metric panel.

## Deterministic analysis

The engine created one six-period standalone panel. Receivables-days and inventory-days were tested; neither had a flagged period. No finding candidate was generated and none was rejected. Price/volume abstained because matched revenue and volume-growth inputs are required. Cash-conversion abstained because matched operating-cash-flow and EBITDA inputs are required. Margin-versus-input-cost abstained because matched gross-margin and input-cost-index disclosures are required. The company result is `no_reliable_finding`; the existing thresholds were not changed.
