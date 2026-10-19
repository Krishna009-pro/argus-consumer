# ARGUS-Consumer implementation status

Updated 2026-10-20 from the current ledger, generated analyses, tests, dashboard run, evaluation, and `config/metrics.yaml`. Detection thresholds were not changed. The dashboard import fix is commit `992eab9`; the previous status snapshot was commit `07b0f65`.

## Current verified-data results

| Company | Verified observations | Panels | Generated candidates | Rejected candidates | Current result |
|---|---:|---:|---:|---:|---|
| Hindustan Unilever Limited | 30 | 7 | 0 | 0 | `no_reliable_finding` |
| ITC Limited | 38 | 12 | 0 | 0 | `no_reliable_finding` |
| Britannia Industries Limited | 18 | 1 | 0 | 0 | `no_reliable_finding` |
| Marico Limited | 6 | 1 | 0 | 0 | `no_reliable_finding` |

HUL has one six-period standalone, pre-demerger panel with FY2020–FY2025 revenue, inventory, and trade receivables. Receivables-days has one flagged period (FY2025); the unchanged persistence rule requires three consecutive flagged periods, so no candidate is generated. Inventory-days remains within its expected range. The FY2025–FY2026 continuing-operations revenue and balance-sheet cohorts are kept separate from the pre-demerger series.

ITC's pre-demerger standalone panel now contains seven consecutive comparable fiscal periods (FY2018–FY2024), with revenue, inventory, and receivables. Date metadata for L0045–L0056 was corrected after checking the 2021 report's PDF pp.178–179 and the 2023 report's pp.184–185. Values and source hashes were not changed. Receivables-days and inventory-days are tested; each has a gap flag only for FY2023, short of the unchanged three-consecutive-period persistence rule. HUL and Britannia are compatible peers, and Britannia's FY2020–FY2025 ratios are now tested, but the distinct tested peer baseline is still below the configured minimum. Continuing/discontinued-operation observations remain in separate scopes. See [itc-peer-data-review.md](reports/itc-peer-data-review.md) and [britannia-peer-review.md](reports/britannia-peer-review.md) for page-level evidence and current abstentions.

All four companies currently return `no_reliable_finding`. HUL price/volume lacks a verified, scope-matched volume series; shorter HUL cohorts also abstain on absent matched inputs or insufficient history. ITC's corrected seven-period historical panel tests receivables-days and inventory-days; each has one FY2023 gap flag, and neither meets three-period persistence. Britannia now has six fully verified standalone periods (FY2020–FY2025); receivables-days and revenue-based inventory-days are tested with no flagged periods. Marico has two verified consolidated periods, so receivables-days and inventory-days abstain at 2 of 6; its consolidated basis and short history make it incompatible with the current standalone peer series. HUL and ITC each list two eligible comparison companies (the other and Britannia), still below the required three independent peer gaps. No missing value was replaced with zero. No company-specific logic was added to the analysis engine.

Detailed HUL page-level source review and coverage are in [hul-phase2-review.md](reports/hul-phase2-review.md) and [hindustan-unilever-limited-panel-coverage.md](reports/hindustan-unilever-limited-panel-coverage.md). The HUL PDF cache hash and ledger entries retain official source URL, page, snippet, reviewer, and status.

## Verification run

- Tests: **40 passed, 0 failed** (`python scripts/run_tests.py`), including regression coverage for fiscal-period alignment, six verified Britannia periods, comparable full-company scope tags, missing-input explanations, and accurate partial-history abstentions.
- Dashboard: Streamlit `AppTest` completed with **0 exceptions**; local `/_stcore/health` returned **HTTP 200 `ok`** on port 8765. Existing Streamlit `use_container_width` deprecation warnings remain. The `eval` import failure was fixed by adding the repository root to the app's import path.
- Online intake follow-up: Dabur's official FY2025-26 annual report (623 PDF pages; SHA-256 `e2677edfd9cc5a5035df98140ab2b8b54ab6c463d3456dca12d9c1980c9391b3`) completed extraction and yielded six financial-statement candidates. Visual page review confirmed the printed table values and standalone/consolidated designations on PDF pages 330, 411, and 412. The parser had incorrectly taken years from the annual-report title instead of table columns; this was fixed generically, with a regression test. The refreshed manifest retains the old mislabeled rows as `ambiguous` and adds six correctly period-labeled rows as `unverified`. None have been approved into the ledger, and no Dabur dossier or analysis has been generated. The MDA PDF produced zero supported statement candidates; the dashboard now explains this and hides the empty review command. Intake and saved-dossier companies are explicitly distinguished.
- Synthetic evaluation: canary recall **100%** (20 planted cases), false-positive rate **5%** (1 of 20 clean cases), missing-data abstain correctness **100%** (4/4), determinism **100%**, window stability **72.5%**. These are synthetic measurements only.
- Latest evaluation: `python scripts/argus.py eval` reported M07 canary recall **100% (20/20)**, M08 false-positive rate **5% (1/20)**, M09 gap-start error **0 periods**, M06 missing-data abstain correctness **100% (4/4)**, M13 window stability **72.5%**, and M14 determinism **100%**. All canary and missing-data figures are synthetic. Evidence grounding: **94/94** checked claims mapped to ledger evidence (M02 **100%**, M03 **0** unsupported claims). M01 remains unavailable (**0/0 published figures compared**); blind-baseline metrics remain unavailable.
- Latest company runs: HUL **30 verified entries used, 7 panels**; ITC **38, 12**; Britannia **18, 1**; Marico **6, 1**. Each generated **0 candidates and 0 rejected candidates** and returns `no_reliable_finding`. HUL receivables-days flags FY2025 only; ITC receivables-days and inventory-days each flag FY2023 only; Britannia's two tested ratios flag no periods; Marico's ratios abstain with two of six usable periods. HUL and ITC each see two compatible peers, still below three. These are screening outputs, not real discoveries.
- Marico source review: six consolidated FY2024–FY2025 observations were visually checked on official FY2024–25 report PDF p.170 (printed pp.336–337); cache SHA-256 `74e0f6c239f6b611a1d66f361988a65f52bdfb51956ada929de3f4857b1e3474`. The four extraction candidates were linked to the matching ledger observations without duplicates using the new generic `link-candidate` command; revenue was recorded from the same rendered source page. Details and exact observations are in [marico-peer-review.md](reports/marico-peer-review.md).
- Real-company reconciliation: unavailable (0 published figures compared). Blind human baseline review: unavailable.

## Remaining before project completion

- Add historical standalone Marico data or another independently reviewed consumer peer with six or more comparable periods. Marico is now an end-to-end dossier but has only two verified periods, on a consolidated basis, so HUL/ITC's standalone peer gate still sees only two compatible peer companies. The M05 four-company floor is met; configured-universe breadth is incomplete. M01 still needs a published-figure reconciliation set covering at least six comparable periods per company.
- Obtain and review a six-period volume-growth series only if its definition and reporting perimeter match the revenue growth input. Current HUL disclosures use underlying growth measures with acquisition/disposal adjustments, so unreviewed figures must not be paired with reported revenue as if automatically comparable.
- Add independent, source-backed red-team evidence for seasonality, one-offs, accounting changes, acquisitions/demergers, pricing lags, and sector movements.
- Measure real-world reconciliation, blind human-baseline results, and longitudinal outcomes. Synthetic evaluation is not real-company validation.
- Improve filing discovery and automate extraction-to-source reconciliation. Extraction candidates remain unverified until a reviewer checks the original source.

There is no validated real-company discovery at this time. A finding requires the existing validation gate to pass with traceable evidence; thresholds remain unchanged.

## Antigravity handoff: remaining implementation work

Use this section as the handoff checklist. Work in small tasks, preserve the hard rules below, and update this file with measured results after each task. Do not treat metric targets as permission to weaken validation or to manufacture a finding.

### Hard constraints

- Do not change `config/metrics.yaml`, the detection thresholds, or validation-gate constants to improve a score.
- Do not add company names, tickers, or company-specific rules to reusable code under `src/`.
- Do not let an LLM author, infer, interpolate, or calculate a numeric observation. Numeric outputs must be computed in Python and trace to ledger IDs.
- Keep machine-extracted claims unverified until a reviewer checks the original public source, exact value, units, period, basis, scope, page, and snippet. Keep unresolved conflicts/missing values unresolved; never substitute zero.
- Cache source files content-addressably and validate SHA-256 before use. Keep the source URL, page, snippet, reviewer, review status, and reporting/comparability metadata.
- A real finding must pass the existing independent-source, persistence, peer, data-integrity, alternative-explanation, and multiple-testing gates. Otherwise report the exact abstention or rejection reason.

### Recommended work order and acceptance checks

1. **Complete comparable peer panels.** ITC's pre-demerger standalone history is aligned for FY2018–FY2024; Britannia's standalone history is now verified for FY2020–FY2025 from official reports. Add approved Track C peers until at least three independent, compatible peers can contribute tested angle values. Marico now has six visually verified consolidated observations for FY2024–FY2025, but is not a six-period peer panel and is basis-mismatched with the standalone histories; do not treat it as an eligible peer panel yet. Do not sum discontinued and continuing operations unless the report itself provides an explicitly comparable total and the methodology records that choice. Acceptance: peer matching lists only compatible, traceable panels; peer-gap counts show actual unique companies and periods; incompatible rows remain excluded.
2. **Resolve price/volume comparability.** Determine whether the disclosed volume-growth measure is on the same reporting perimeter and growth basis as the revenue measure used by the engine. Underlying sales/volume growth may exclude acquisitions/disposals while reported revenue may include them. If the measures are not demonstrably comparable, keep `price_volume` abstained. If a reusable model change is needed, implement a generic disclosed-growth-basis contract and tests; do not add HUL-specific handling. Acceptance: six usable, reviewed periods use matched definitions, or the dossier explains the scope mismatch and abstains.
3. **Implement evidence-backed red-team checks.** Retrieve and cache public sources for seasonality, base effects, one-offs, accounting changes, acquisitions/demergers, pricing lags, and sector-wide movement. Record each test's source, page/snippet, decision, and reason; calculate the benign share in deterministic code. LLM classifications may structure text only and must not provide numeric calculations. Acceptance: tests cover supported, unsupported, and missing-source cases; no missing evidence becomes a pass; at least 30% of research queries are tagged disconfirming when queries are issued.
4. **Build real-company reconciliation and breadth evaluation.** Add a reviewed public reference set covering at least four companies and six comparable periods per company, then run the existing reconciliation method against every computed metric. Complete the project-approved Track C list without company-specific code. Acceptance: report matched/compared counts, all exclusions, and per-company results; meet the configured M01 and M05 floors before claiming those gates are satisfied.
5. **Measure blind baselines and practical operation.** Produce blind ARGUS and baseline outputs for at least four companies, collect reviewer scores without revealing system identity, and measure cached end-to-end latency and model API cost only when telemetry is available. Acceptance: publish sample sizes, missing measurements, reviewer rubric, and uncertainty; never convert unavailable to zero.
6. **Complete regression and dashboard verification.** For each code/data-contract change, run `python scripts/run_tests.py`; at final integration run `python scripts/argus.py eval`, regenerate HUL and ITC dossiers, and use `streamlit run app/streamlit_app.py` plus the health endpoint and app-level check. Confirm source links, panel scope, abstentions, and evidence IDs render correctly.

### Accuracy and evaluation matrix

Targets/bounds below are copied from `config/metrics.yaml`; they are acceptance goals, not current performance claims. “Current” reflects the latest local evaluation artifacts checked on 2026-10-20. A blank/unavailable metric must remain labeled unavailable until its specified evaluation data exists.

| Metric | Current result | Configured floor / target / stretch | Antigravity acceptance / evidence |
|---|---|---|---|
| M01 reconciliation rate | Unavailable: 0 published figures compared | 90% / 95% / 99% | Evaluate at least 4 companies × 6 periods × every computed metric; match within max(0.5% of value, one rounding unit); report matched and compared counts. |
| M02 claim grounding | 100% (94/94 checked claims) | 90% / 97% / 100% | Maintain live source URL, PDF page, cached snippet containing the value, and valid hash; expand the audited corpus. |
| M03 unsupported claims | 0 in latest grounding run | 0 / 0 / 0; gate | Keep exactly zero claims without ledger support. |
| M04 LLM-authored numeric tokens | Tests pass; standalone measured score unavailable | 0 / 0 / 0; gate | Keep numeric outputs ledger-grounded and add/report a measurable audit count if possible. |
| M05 companies end to end | 4 dossiers generated (HUL, ITC, Britannia, Marico); configured universe run unavailable | 4 / 6 / 9 companies | The four-company floor is met for dossier generation; breadth across the approved Track C universe remains incomplete. Record successes, abstentions, and failures. |
| M06 missing-data abstain correctness | 100% (4/4 synthetic cases) | 95% / 100% / 100% | Expand missing, ambiguous, conflicting, and tampered-source cases; no fabricated zero or interpolation. |
| M07 synthetic canary recall | 100% (20/20 planted cases) | 70% / 85% / 95% | Preserve ground-truth labels, anomaly type, and gap-start error; separately label this as synthetic. |
| M08 synthetic false-positive rate | 5% (1/20 clean cases) | 20% / 10% / 5% | Keep the clean-case denominator visible and avoid tuning thresholds on the evaluation set. |
| M09 gap-start error | 0 periods (median absolute error) | 1.0 / 0.5 / 0 periods | Report number of detected cases and median absolute period error on the fixed synthetic canary set. |
| M10 red-team rejection band | Unavailable: no candidate cases exercised | 20–80% sanity band | Evaluate on a labeled candidate set; report count and denominator. This is diagnostic, not a target to optimize in isolation. |
| M11 baseline advantage | Unavailable: no blind human review | 0.5 / 1.5 / 2.5 rubric points | Blindly compare ARGUS with the best baseline for at least 4 companies; document the 0–6 rubric and reviewer protocol. |
| M12 Strong-label precision | Unavailable: no Strong real findings / blind labels | 80% / 90% / 100% | Report Strong count and reviewer-confirmed count; no precision claim without a nonzero labeled sample. |
| M13 window stability | 72.5% | 60% / 80% / 95% | Investigate instability without threshold changes; compare verdict class across all three configured history windows. |
| M14 determinism | 100% (two cache reruns) | 100% / 100% / 100%; gate | Keep numeric outputs byte/value-stable across cache reruns and record the compared outputs. |
| M15 cached live latency | Not measured by the official evaluation protocol | 600 / 240 / 120 seconds | Measure wall-clock company-input-to-dossier latency using the standard cached run; report sample count and environment. |
| M16 disconfirming query share | Unavailable: no retrieved candidate research | 20% / 30% / 40% | Log query tags and calculate disconfirming share; meet at least the 20% floor when candidate research is run. |
| M17 API cost per run | Unavailable: no cost telemetry recorded | $3 / $1 / $0.50 | Record provider-reported cost per company run; label providers without cost telemetry unavailable. |
| M18 hindsight persistence (optional) | Unavailable: no as-of historical evaluation set | 50% / 65% / 80% | If implemented, use only data available at the historical cutoff and report sample count plus next-two-period persistence. |

The synthetic M06–M09 results do not establish real-world accuracy. Real reconciliation (M01), baseline advantage/Strong precision (M11/M12), and hindsight persistence (M18) require labeled public evidence and/or blind human review. Keep every metric's status, numerator/denominator, data type (synthetic or real), and source artifact in the final report.
