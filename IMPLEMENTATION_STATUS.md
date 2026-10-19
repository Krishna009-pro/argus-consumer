# ARGUS Phase 2 implementation status

Updated 2026-10-19. The development plan and `config/metrics.yaml` remain the acceptance source; no thresholds were changed. There is no Git metadata in this workspace, so repository history/diff comparison is unavailable.

## Completed in this implementation

- Added a public-company source catalog for ITC and HUL. It records official source URLs only; it does not claim those files were downloaded.
- Added content-hash local PDF/CSV import as unverified candidates and explicit human review before ledger insertion. Ledger writes require a verified reviewer, period type, currency, basis, exact cached snippet, and supported numeric value.
- Built verified-data panels keyed by company, period type, currency, consolidation basis, reporting scope and comparability cohort. Duplicate metric/period observations and mixed units become unavailable instead of being selected arbitrarily. Cross-company peer selection ignores company-local cohort labels while requiring compatible basis, currency, period type, periods and reporting scope.
- Connected deterministic price/mix, receivable days, inventory days, cash conversion, and gross-margin/input-cost calculations to panel values with period IDs and abstention reasons.
- Connected candidate screening, persistence, peer adjustment and evidence gates to the CLI. Research query plans are logged; without retrieval, explanations and red-team tests are explicitly marked unavailable/not tested.
- Generated ITC and HUL dossier JSON/Markdown from the same CLI. Added a shared PDF exporter used by the CLI and Streamlit download.
- Added panel formula, duplicate-observation, local-import/reviewer-flow, peer-compatibility and multi-panel evidence tests; the full 24-test suite passes. Synthetic evaluation runs through the CLI.

## Measured this run

| Result | Measurement |
|---|---:|
| Tests | 24 passed |
| Synthetic canary recall | 100% (20 planted cases; synthetic only) |
| Synthetic canary false-positive rate | 5% (1/20 clean cases) |
| Synthetic gap-start error | 0 periods |
| Missing-data abstain correctness | 100% (4/4 synthetic cases) |
| ITC verified observations / panels | 0 / 0 |
| HUL verified observations / panels | 12 / 6 |
| Real reconciliation | unavailable; 0 compared published figures |
| Human baseline review | unavailable |

Streamlit started successfully and its local health endpoint returned `ok`. The user supplied HUL FY2025–26 annual report was imported to the content-addressed cache and visually checked on the cited statement pages. Twelve observations were recorded: two years of continuing-operations revenue for standalone and consolidated bases, plus FY2025/FY2026 closing inventory and receivables in separate pre-/post-demerger cohorts. The current run creates six panels and abstains on every angle; it is not a real discovery. See `data/review_notes/hul-fy2025-26-source-review.md` and `reports/hindustan-unilever-limited-panel-coverage.md`.

## Outstanding source and plan gaps

- The official HUL file request previously returned HTTP 403 from this host; the user subsequently supplied a local copy, which is now cached and traced. No earlier annual reports were supplied, so the panel remains only two revenue years and isolated balance-sheet snapshots. The ITC request did not complete.
- Automated table layout resolution and source retrieval are not complete. PDF extraction yields candidate snippets for manual review; it does not establish statement alignment, units, period, or consolidation basis.
- Peer matching applies generic scope/basis/currency/period compatibility, but there is no reviewed business-profile fact set or real peer corpus. Peer gates abstain without at least three compatible panels.
- No retrieved-source research, human-tested alternative explanations, or LLM endpoint was available. Query planning is not evidence, and red-team outcomes remain not tested.
- Real-company reconciliation, same-company baseline comparison, hindsight evaluation, and longitudinal falsification watch remain unavailable without verified source corpora and review.
- The dashboard now includes panel inspection, angle abstentions, an expected-range view when an angle is testable, and a Proof Panel comparing ARGUS with the existing ratio screen. Plain-LLM outputs remain unavailable without configured model output and blind human scoring.
- Runtime company-name search and automated filing discovery remain incomplete. The public HTML search endpoint returned a challenge response; no search provider credentials are configured, and the app does not bypass that challenge.
- No residual chart is drawn for HUL because all angles abstain. The UI preserves missing values instead of drawing zeros or synthetic substitutes.

## Generated outputs

- `reports/hindustan-unilever-limited.{md,json}` and `reports/hindustan-unilever-limited-analysis.json`
- `reports/hindustan-unilever-limited-panel-coverage.md`
- `data/review_notes/hul-fy2025-26-source-review.md`
- `demo/ARGUS-Consumer-Prototype-Demo.mp4` (118 seconds; narrated prototype walkthrough)
- Streamlit panel/proof view and peer matching are exercised by the current 24-test suite; local preview rendered with HUL panels and ratio screen values.
- `eval/results/summary.json` and `eval/results/scoreboard.md`

The HUL dossier is based on 12 verified source observations. Its output is an abstention, not a company discovery. ITC still has no verified ledger observations. Synthetic evaluation values are kept labeled as synthetic.
