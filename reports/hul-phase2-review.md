# HUL Phase 2 — verified historical data review

Reviewed: 2026-10-19  
Company: Hindustan Unilever Limited  
Result: `no_reliable_finding`; detection thresholds are unchanged. Dossier aggregation and ledger-reference formatting were improved and regression-tested.

## Verified standalone historical observations

All values below are INR crore. FY periods end on 31 March. Source page numbers are the physical PDF viewer pages; printed footer pages are also shown because these reports often place two numbered pages on one PDF page. `Lxxxx` IDs point to verified rows in `data/ledger.jsonl`.

| Period | Revenue from operations | Inventory | Trade receivables | Basis | Ledger IDs |
|---|---:|---:|---:|---|---|
| FY2020 | 38,785 (PDF p. 66; print pp. 126–127) | 2,636 (PDF p. 65; print pp. 124–125) | 1,046 (PDF p. 65; print pp. 124–125) | Standalone | L0013–L0015 |
| FY2021 | 45,996 (PDF p. 66; print pp. 126–127) | 3,383 (PDF p. 65; print pp. 124–125) | 1,648 (PDF p. 65; print pp. 124–125) | Standalone | L0016–L0018 |
| FY2022 | 51,193 (PDF p. 72; print pp. 138–139) | 3,890 (PDF p. 71; print pp. 136–137) | 1,932 (PDF p. 71; print pp. 136–137) | Standalone | L0019–L0021 |
| FY2023 | 59,144 (PDF p. 103; print pp. 200–201) | 4,031 (PDF p. 102; print pp. 198–199) | 2,735 (PDF p. 102; print pp. 198–199) | Standalone | L0022–L0024 |
| FY2024 | 60,469 (PDF p. 140; print pp. 274–275) | 3,812 (PDF p. 139; print pp. 272–273) | 2,690 (PDF p. 139; print pp. 272–273) | Standalone | L0025–L0027 |
| FY2025 | 61,469 (PDF p. 146; print pp. 286–287) | 4,161 (PDF p. 145; print pp. 284–285) | 3,450 (PDF p. 145; print pp. 284–285) | Standalone | L0028–L0030 |

Each value was manually compared to the statement title, line item, reported year column, units and basis on its cached PDF page. Revenue rows come from the Standalone Statement of Profit and Loss; inventory and receivables rows come from the Standalone Balance Sheet. The exact snippets, reviewer status, source URL, page, cache path and SHA-256 are retained on each ledger row. Source-page visual checks covered all ten statement pages listed above.

## Verified FY2025–26 observations (separate reporting cohorts)

These twelve rows were already present as manually verified ledger entries L0001–L0012 and have now also been checked against cached standalone and consolidated statement pages. All values are INR crore. FY2025 continuing-operations revenue is a restated comparative; total-scope FY2025 revenue in the preceding table is kept separate.

| Basis | Period | Revenue from operations | PDF page | Inventory | Trade receivables | PDF page |
|---|---|---:|---:|---:|---:|---:|
| Standalone | FY2026 continuing operations | 61,975 | 139 | 4,383 | 3,037 | 138 |
| Standalone | FY2025 continuing operations comparative | 59,676 | 139 | 4,161 | 3,450 | 138 |
| Consolidated | FY2026 continuing operations | 64,468 | 184 | 4,789 | 3,379 | 183 |
| Consolidated | FY2025 continuing operations comparative | 61,328 | 184 | 4,415 | 3,819 | 183 |

Location: `Revenue from operations` under the statement's **Continuing Operations** heading in the standalone or consolidated Statement of Profit and Loss; `Inventories` and `Trade receivables` rows in the corresponding Balance Sheet, with the March 2026 and March 2025 columns explicitly labelled. PDF viewer pages 138–139 carry printed pages 272–275; pages 183–184 carry printed pages 362–365.

## Filing provenance and cached file hashes

| Report | BSE filing copy | Cache SHA-256 |
|---|---|---|
| Integrated Annual Report 2020–21 (FY2020–FY2021) | [Official BSE PDF](https://www.bseindia.com/bseplus/AnnualReport/500696/68482500696.pdf) | `dc4c172c0bbed90da13345786a8b7d73c1cd1d65775bd9ab14da778c41f03808` |
| Integrated Annual Report 2021–22 (FY2022) | [Official BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/7bbfea5f-ec6b-41a5-9ea8-0694a17d29ab.pdf) | `fb213890754c0d34ea65946c4ef36f209e8c1ebb0da12c3a3a054b5dd9db0307` |
| Integrated Annual Report 2022–23 (FY2023) | [Official BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/dbf3868a-97f3-43ed-b5ce-47e83261fdc4.pdf) | `f437de00ba2c7d2fa16ab86db347e8d941048ede1922cbf30f0651eb08792311` |
| Integrated Report 2023–24 (FY2024) | [Official BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/02d8d87d-90ce-4191-8b3f-4167267aee8a.pdf) | `ffb3d9f6bde2d6fa5882011ad4d394f1d6ddbdfcd3d6080617d652a90fa10595` |
| Integrated Report 2024–25 (FY2025) | [Official BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/770bf03e-526d-45d8-8364-13f7fc523289.pdf) | `f53ee0747f42111f1c9a10b345c1573506d988ea9951001e6c9bdb37099db892` |

The supplied FY2025–26 annual report is separately cached at `data/incoming/hul-annual-report-2025-26.pdf`, SHA-256 `98219f80b28472d4d11c893274e0537b5098c98f34dcc30c7f905db3cb7a929b`, from [HUL's official report URL](https://www.hul.co.in/files/annual-report-2025-26.pdf). Its already verified observations are L0001–L0012.

## Scope and comparability

- L0013–L0030 form one panel: standalone, annual, `total_operations_pre_demerger`, cohort `pre_demerger_standalone_FY2020_FY2025`.
- HUL FY2025–26 presents the ice-cream undertaking as discontinued operations and re-presents FY2025 continuing-operation comparatives. The standalone statement on FY2025–26 PDF p. 139 reports FY2025 continuing-operations revenue of INR 59,676 crore; the FY2024–25 full-scope standalone report reports INR 61,469 crore. Both are retained under their different scopes. They are not combined into one series.
- FY2026 standalone and consolidated balance-sheet observations remain in the post-demerger FY2026 cohort. FY2025 comparative balance-sheet observations remain in a pre-demerger cohort. Neither short balance-sheet cohort has enough matched revenue periods to compute days.
- The first six-year cohort is standalone only. No comparable six-year consolidated panel or eligible peer panel was assembled. Acquisition and portfolio changes, discontinued operations, and the demerger limit comparisons beyond the explicitly separated cohorts.
- Inventory days uses revenue as its denominator because a verified cost-of-goods-sold series was not added to this cohort. This makes it a revenue-based inventory-days ratio, not a cost-of-sales inventory turnover measure.

## Historical panel coverage

| Panel | Coverage | Status |
|---|---|---|
| Standalone, pre-demerger total operations | FY2020–FY2025: revenue, inventory and receivables all present (6/6 each) | Ready for receivables-days and revenue-based inventory-days screening |
| Standalone, continuing operations | FY2025–FY2026 revenue only (2 periods) | Under six periods; no matching balance-sheet metrics in this cohort |
| Consolidated, continuing operations | FY2025–FY2026 revenue only (2 periods) | Under six periods; no matching balance-sheet metrics in this cohort |
| Standalone, pre-demerger balance sheet | FY2025 inventory and receivables only | Missing matched revenue/history in this cohort |
| Standalone, post-demerger balance sheet | FY2026 inventory and receivables only | Missing matched revenue/history in this cohort |
| Consolidated, pre-demerger balance sheet | FY2025 inventory and receivables only | Missing matched revenue/history in this cohort |
| Consolidated, post-demerger balance sheet | FY2026 inventory and receivables only | Missing matched revenue/history in this cohort |

No missing observation was changed to zero. FY2020–FY2025 revenue, inventory and receivables have no gaps in the selected standalone cohort. Historical consolidated observations and peers are absent, not zero.

## Deterministic analysis

Command: `python scripts/argus.py run --company "Hindustan Unilever Limited"`  
Output: `no_reliable_finding`; 30 verified ledger entries; 7 panels; 0 engine-generated candidates; 0 rejected engine candidates.

The historical panel reports receivables days of 9.8707, 13.0777, 13.7749, 16.8787, 16.2817 and 20.4859 for FY2020–FY2025. FY2025 is above the engine's historical expected band (7.7908–19.0617), but this is one flagged period; the unchanged validation rule requires at least three consecutive flagged periods before generating a candidate. Therefore no engine candidate reached the validation gate. This is a screening deviation, not a discovery.

Inventory days, using revenue as denominator, are 24.8750, 26.8457, 27.7352, 24.8768, 23.0728 and 24.7078. FY2025 lies within the engine's expected range (22.9395–28.7831). No inventory-days gap was flagged.

### Abstentions

- Six shorter continuing-operations or balance-sheet panels abstain on all five angles (30 abstentions). Exact reasons in the generated analysis are either `Fewer than six usable disclosed periods.` or, for inventory days, `Inventory, a same-unit positive denominator, and exact period day count are required.` The latter applies where inventory, revenue or duration is missing from the same panel.
- The six-year historical panel abstains on `price_volume` because no verified volume-growth series exists; on `cash_conversion` because no matched operating-cash-flow and EBITDA series exists; and on `margin_vs_input_cost` because matched gross-margin and input-cost-index series are absent. The engine records `Fewer than six usable disclosed periods.` for each angle.
- The historical panel's receivables-days and inventory-days angles are tested. The reported receivables outlier is not a candidate because the persistence condition is not met.
- There are no rejected engine candidates: no candidate was generated. There are no eligible peer panels, so peer-adjusted validation is unavailable. The dossier also states that the red-team review was not run and independently retrieved source evidence is unavailable.
- The peer-adjusted deviation function requires at least three peer-gap observations and the engine counts each peer company once per comparison period. The single-ITC dataset suggested in `CODEX_TASKS.md` would remain insufficient to satisfy that gate. Peer scope and standalone basis must also match the HUL comparison cohort; no peer values were added without verified, comparable source panels.
- HUL reported underlying volume growth for its domestic consumer business, while the historical revenue series is full standalone revenue. A volume series must have compatible scope and six usable periods before it can support `price_volume`; the incomplete or differently scoped values suggested for FY2021–FY2025 were not inserted into the ledger.

The complete period-by-period panel output and exact abstention strings are in `reports/hindustan-unilever-limited-analysis.json`; the rendered dossier is `reports/hindustan-unilever-limited.md`.

## Extractor candidates and review audit

After the generic extractor update, the latest pass emitted 12 unverified proposals from dated standalone/consolidated statement columns (PDF pp. 138–139 and 183–184). They match values already present as reviewed entries L0001–L0012, but the new proposals were not automatically approved. The 68-row candidate manifest contains those 12 current `unverified` proposals, 50 older proposals marked `ambiguous` because the safer extractor no longer emits them, and 6 retained `rejected` legacy note-reference proposals. Note references (11, 12, 25, 27) remain audit-only and never enter the evidence ledger as financial data.

## Verification status

- Existing tests: 27 passed, 0 failed (`python scripts/run_tests.py`).
- Streamlit health endpoint: `http://127.0.0.1:8765/_stcore/health` returned HTTP 200 `ok` after starting the existing dashboard app.
- Detection thresholds: unchanged. General-purpose dossier aggregation and provenance formatting changes were made; no HUL-specific engine rules were added.
- No finding cleared the validation gate. No candidate was generated because the persistence requirement was not met; no peer-adjusted or independent alternative-explanation result was available.

