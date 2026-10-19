# ARGUS-Consumer implementation status

Updated 2026-10-19 from the current ledger, generated analyses, tests, dashboard run, evaluation, and `config/metrics.yaml`. Detection thresholds were not changed. The dashboard import fix is commit `992eab9`; the previous status snapshot was commit `07b0f65`.

## Current verified-data results

| Company | Verified observations | Panels | Generated candidates | Rejected candidates | Current result |
|---|---:|---:|---:|---:|---|
| Hindustan Unilever Limited | 30 | 7 | 0 | 0 | `no_reliable_finding` |
| ITC Limited | 32 | 13 | 0 | 0 | `no_reliable_finding` |

HUL has one six-period standalone, pre-demerger panel with FY2020–FY2025 revenue, inventory, and trade receivables. Receivables-days has one flagged period (FY2025); the unchanged persistence rule requires three consecutive flagged periods, so no candidate is generated. Inventory-days remains within its expected range. The FY2025–FY2026 continuing-operations revenue and balance-sheet cohorts are kept separate from the pre-demerger series.

ITC's pre-demerger panel now contains five periods by the ledger's FY labels (FY2020–FY2024), with revenue, inventory, and receivables, including three visually reviewed FY2024 values from the official 2024 report (L0062–L0064). It is still below the six-period minimum. The older ITC rows L0045–L0056 contain period labels and date metadata that do not consistently agree; FY2023 and FY2024 date spans overlap. This historical metadata issue must be reconciled against the cached reports before ITC is treated as a date-aligned peer. Continuing/discontinued-operation observations and balance sheets from the later report remain in separate cohorts. ITC is structurally eligible as an HUL peer in compatible panels, but no peer angle has six usable periods and no peer-gap observation is available for the gate. See [itc-peer-data-review.md](reports/itc-peer-data-review.md) for the new page-level provenance and scope limitations.

Both companies currently abstain. HUL price/volume lacks a verified, scope-matched volume series; its other abstentions cite missing matched inputs or fewer than six periods. ITC's four-period historical panel is below the six-period minimum. No missing value was replaced with zero. No company-specific logic was added to the analysis engine.

Detailed HUL page-level source review and coverage are in [hul-phase2-review.md](reports/hul-phase2-review.md) and [hindustan-unilever-limited-panel-coverage.md](reports/hindustan-unilever-limited-panel-coverage.md). The HUL PDF cache hash and ledger entries retain official source URL, page, snippet, reviewer, and status.

## Verification run

- Tests: **33 passed, 0 failed** (`python -m unittest discover -s tests -v`).
- Dashboard: Streamlit `AppTest` completed with **0 exceptions**; local health endpoint returned **HTTP 200 `ok`**. Existing Streamlit `use_container_width` deprecation warnings remain. The `eval` import failure was fixed by adding the repository root to the app's import path.
- Online intake follow-up: Dabur's official FY2025-26 annual report (623 PDF pages; SHA-256 `e2677edfd9cc5a5035df98140ab2b8b54ab6c463d3456dca12d9c1980c9391b3`) completed extraction and yielded six financial-statement candidates. Visual page review confirmed the printed table values and standalone/consolidated designations on PDF pages 330, 411, and 412. The parser had incorrectly taken years from the annual-report title instead of table columns; this was fixed generically, with a regression test. The refreshed manifest retains the old mislabeled rows as `ambiguous` and adds six correctly period-labeled rows as `unverified`. None have been approved into the ledger, and no Dabur dossier or analysis has been generated. The MDA PDF produced zero supported statement candidates; the dashboard now explains this and hides the empty review command. Intake and saved-dossier companies are explicitly distinguished.
- Synthetic evaluation: canary recall **100%** (20 planted cases), false-positive rate **5%** (1 of 20 clean cases), missing-data abstain correctness **100%** (4/4), determinism **100%**, window stability **72.5%**. These are synthetic measurements only.
- Latest evaluation: `python scripts/argus.py eval` reported M07 canary recall **100% (20/20)**, M08 false-positive rate **5% (1/20)**, M09 gap-start error **0 periods**, M06 missing-data abstain correctness **100% (4/4)**, M13 window stability **72.5%**, and M14 determinism **100%**. All canary and missing-data figures are synthetic. Evidence grounding: **70/70** checked claims mapped to ledger evidence (M02 **100%**, M03 **0** unsupported claims).
- Latest company runs: HUL **30 verified entries, 7 panels, 0 candidates, 0 rejected**, `no_reliable_finding`; ITC **32 verified entries, 13 panels, 0 candidates, 0 rejected**, `no_reliable_finding`. These are run outputs, not real discoveries.
- Real-company reconciliation: unavailable (0 published figures compared). Blind human baseline review: unavailable.

## Remaining before project completion

- Add additional reviewed peer-company histories with compatible scope, basis, currency, and periods. ITC has five periods by current ledger labels, still below six. Resolve the FY2020–FY2023 date-metadata mismatch in L0045–L0056 against their cached source reports before counting ITC as a date-aligned peer. One additional period alone would not meet the requirement for at least three independent compatible peers.
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

1. **Complete comparable peer panels.** Extend ITC's pre-demerger history from four periods only where official filings support the same standalone/consolidated basis, reporting scope, currency, and period. Add other listed consumer peers from the project-approved Track C universe until at least three independent, compatible peers can contribute tested angle values. Do not sum discontinued and continuing operations unless the report itself provides an explicitly comparable total and the methodology records that choice. Acceptance: peer matching lists only compatible, traceable panels; peer-gap counts show the actual unique companies and periods; incompatible rows remain excluded.
2. **Resolve price/volume comparability.** Determine whether the disclosed volume-growth measure is on the same reporting perimeter and growth basis as the revenue measure used by the engine. Underlying sales/volume growth may exclude acquisitions/disposals while reported revenue may include them. If the measures are not demonstrably comparable, keep `price_volume` abstained. If a reusable model change is needed, implement a generic disclosed-growth-basis contract and tests; do not add HUL-specific handling. Acceptance: six usable, reviewed periods use matched definitions, or the dossier explains the scope mismatch and abstains.
3. **Implement evidence-backed red-team checks.** Retrieve and cache public sources for seasonality, base effects, one-offs, accounting changes, acquisitions/demergers, pricing lags, and sector-wide movement. Record each test's source, page/snippet, decision, and reason; calculate the benign share in deterministic code. LLM classifications may structure text only and must not provide numeric calculations. Acceptance: tests cover supported, unsupported, and missing-source cases; no missing evidence becomes a pass; at least 30% of research queries are tagged disconfirming when queries are issued.
4. **Build real-company reconciliation and breadth evaluation.** Add a reviewed public reference set covering at least four companies and six comparable periods per company, then run the existing reconciliation method against every computed metric. Complete the project-approved Track C list without company-specific code. Acceptance: report matched/compared counts, all exclusions, and per-company results; meet the configured M01 and M05 floors before claiming those gates are satisfied.
5. **Measure blind baselines and practical operation.** Produce blind ARGUS and baseline outputs for at least four companies, collect reviewer scores without revealing system identity, and measure cached end-to-end latency and model API cost only when telemetry is available. Acceptance: publish sample sizes, missing measurements, reviewer rubric, and uncertainty; never convert unavailable to zero.
6. **Complete regression and dashboard verification.** For each code/data-contract change, run `python scripts/run_tests.py`; at final integration run `python scripts/argus.py eval`, regenerate HUL and ITC dossiers, and use `streamlit run app/streamlit_app.py` plus the health endpoint and app-level check. Confirm source links, panel scope, abstentions, and evidence IDs render correctly.

### Accuracy and evaluation matrix

Targets/bounds below are copied from `config/metrics.yaml`; they are acceptance goals, not current performance claims. “Current” reflects the latest local evaluation artifacts checked on 2026-10-19. A blank/unavailable metric must remain labeled unavailable until its specified evaluation data exists.

| Metric | Current result | Configured floor / target / stretch | Antigravity acceptance / evidence |
|---|---|---|---|
| M01 reconciliation rate | Unavailable: 0 published figures compared | 90% / 95% / 99% | Evaluate at least 4 companies × 6 periods × every computed metric; match within max(0.5% of value, one rounding unit); report matched and compared counts. |
| M02 claim grounding | 100% (61/61 checked claims) | 90% / 97% / 100% | Maintain live source URL, PDF page, cached snippet containing the value, and valid hash; expand the audited corpus. |
| M03 unsupported claims | 0 in latest grounding run | 0 / 0 / 0; gate | Keep exactly zero claims without ledger support. |
| M04 LLM-authored numeric tokens | Tests pass; standalone measured score unavailable | 0 / 0 / 0; gate | Keep numeric outputs ledger-grounded and add/report a measurable audit count if possible. |
| M05 companies end to end | 2 dossiers generated (HUL, ITC); configured universe run unavailable | 4 / 6 / 9 companies | Complete the Track C company list with no per-company source-code changes; record list, successes, abstentions, and failures. |
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
