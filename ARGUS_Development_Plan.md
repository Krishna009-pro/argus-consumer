# ARGUS-Consumer: Development Plan and Metric Bounds

Audience: a coding agent (Codex, Antigravity or similar) and the human team.
Event: ATMOS 2026 "Finding the Next Signal", Track C (Consumer, FMCG & Retail).
Dates: Round 1 report due Mon 19 Oct 2026, 11:59 PM IST. Results Fri 23 Oct. Finals Sun 25 Oct (live demo on a company the judges choose).

---

## 0. How to use this file (read first)

1. Work on ONE task ID at a time from Section 7. Finish its acceptance test before starting the next.
2. Never change a number in `config/metrics.yaml` to make a test pass. Fix the code.
3. Run `make test` after every task and `make eval` at the end of each day.
4. If a task is blocked by missing public data, implement the abstain path (Section 3, rule R4) and move on. Do not invent data.
5. Prefer small plain Python over frameworks. If a framework (LangGraph or similar) is not saving time by day 2, use a sequential pipeline.

Task prompt template for the agent:

```
Implement task {ID} from ARGUS_Development_Plan.md.
Read Section 3 (hard rules) and Section 4 (data contracts) first.
Write the code, then write tests that satisfy the task's acceptance line.
Do not touch config/metrics.yaml. Report which metric IDs the task moves.
```

---

## 1. What we are building (one paragraph)

An autonomous agent that takes any listed Track C company, profiles its business model, computes what its numbers SHOULD look like (a range, not a point), finds gaps that are persistent and company-specific, then tries to explain them and to disprove its own explanation. It publishes a finding only if it survives a validation gate, and every number links to a source. If evidence is thin it says "no reliable finding".

Design principle: **ordinary code computes every number. LLMs plan searches, read documents and argue. LLMs never produce or edit a number.**

---

## 2. Success definition: lower bound, target, upper bound

Every metric has three bounds. Direction matters (higher or lower is better).

| Tier | Meaning | Dashboard colour |
|---|---|---|
| BELOW_FLOOR | Worse than the lower bound. Not safe to demo. | red |
| FLOOR | Meets the lower bound. Minimum acceptable. | amber |
| TARGET | Meets the target. What we plan for. | green |
| BEYOND | Meets or exceeds the upper bound (stretch). Best case. | gold |

Gate metrics (marked `gate: true`) must be met exactly. Missing a gate means the build is not shippable, whatever else scores.

Honesty rules for results:
- Bounds are goals we set, not results. Never present a bound as a measured result.
- Report counts next to percentages (for example "17 of 20"). Samples are small.
- Every reported number must come from `eval/results/*.json` produced by `make eval`.

---

## 3. Hard rules (the agent must obey these)

- R1. No company-specific code. Company names must not appear in `src/` logic. Test: `tests/test_no_hardcoding.py` greps `src/` for ticker and company names from a list and fails on a match.
- R2. Every number in any output has a ledger entry (Section 4). Test: every numeric token in a dossier maps to a ledger id.
- R3. LLM output must not contain computed numbers. Numbers are inserted by templates from ledger values.
- R4. Missing input means ABSTAIN for that angle. A missing value is never zero and never guessed. The dossier lists what could not be tested.
- R5. Findings need at least 2 independent source layers (filings, management commentary, outside evidence). "Strong" needs 3.
- R6. Public data only. No paid or proprietary datasets.
- R7. No investment recommendation. A gap is never described as an accusation about the company.
- R8. Cache every fetched source file with its hash so results are reproducible offline.

---

## 4. Data contracts (Pydantic v2, `src/argus/schemas.py`)

```python
class LedgerEntry(BaseModel):
    id: str                      # "L0001"
    metric: str                  # "trade_receivables"
    value: float
    unit: str                    # "INR_cr", "pct", "days"
    period: str                  # "FY26-H1", "FY26-Q2"
    source_url: str
    source_type: Literal["filing", "management", "outside"]
    doc_page: int | None
    snippet: str                 # exact text that contains the value
    source_sha256: str           # hash of the cached file
    retrieved_at: datetime

class AngleResult(BaseModel):
    angle: str                   # "price_volume", "working_capital", ...
    status: Literal["tested", "abstained"]
    abstain_reason: str | None
    series: dict[str, list[float]]        # reported, expected_low, expected_high, peer_median
    periods: list[str]
    gap_flags: list[bool]
    persistence_periods: int
    ledger_ids: list[str]

class Candidate(BaseModel):
    id: str
    angles: list[str]            # related angles combined (cross-metric)
    gap_start_period: str
    summary_numbers: dict[str, float]     # code-computed only
    hypotheses: list[str]        # LLM text, no numbers
    red_team_log: list[dict]     # {test, outcome, reason}
    gate: dict                   # persistence, peer, data_quality, alt_explanations, patterns_tested
    state: Literal["explained", "unexplained", "no_reliable_finding", "rejected"]

class Dossier(BaseModel):
    company: str
    discovery: str               # one sentence
    why_it_matters: list[str]    # 3 to 5 bullets
    evidence: list[str]          # ledger ids
    timeline: list[dict]
    numbers: dict[str, float]
    counterargument: str
    falsification_condition: str
    evidence_score: float        # 0 to 100
    evidence_label: Literal["Strong", "Moderate", "Weak"]
    not_tested: list[str]
```

---

## 5. Core algorithms (exact enough to implement)

### 5.1 Metrics (code only)

- Price/mix growth = (1 + revenue_growth) / (1 + volume_growth) - 1. Needs disclosed volume growth. If absent, use industry volume trend from a public source, or abstain.
- Receivable days = trade_receivables / revenue_for_period * days_in_period.
- Inventory days = inventory / cost_of_goods_or_revenue_for_period * days_in_period (state which denominator was used).
- Cash conversion = operating_cash_flow / EBITDA, only for periods where cash flow is disclosed (often half-yearly).
- Margin vs input cost = gross margin change versus a public price index (CPI/WPI component) change.
- Use the finest period each input is actually disclosed. Never interpolate to fake quarters.

### 5.2 Expected range

```
history = metric values for the last N periods (N >= 6 if available, else abstain)
center  = median(history excluding the latest 2 periods)
spread  = 1.4826 * MAD(history excluding the latest 2 periods)
low, high = center - 2*spread, center + 2*spread
peer_adjusted_deviation = (company_gap - median(peer_gaps)) / MAD(peer_gaps)
gap_flag[t] = value[t] outside [low, high]
persistence = longest recent run of consecutive True gap_flags
Candidate only if persistence >= 3 periods AND peer_adjusted_deviation >= 1.5
```

If fewer than 3 peers have data, mark peer check "insufficient" and cap the label at Weak.

### 5.3 Cross-metric links

Combine angles into one candidate when 2 or more angles flag in the same period window. Example: receivable_days up AND inventory_days up AND cash_conversion down. Record which angle flagged first (a sequence is a hypothesis, not proof of cause).

### 5.4 Validation gate (runs after red-team, before claim checking)

Checks, all must pass to publish:
1. persistence >= 3 periods
2. peer-adjusted deviation >= 1.5
3. data quality: all inputs have ledger entries with matching hashes
4. alternative explanations: no benign explanation covers more than 60 percent of the gap (red-team estimate is recorded, and the arithmetic share uses code)
5. multiple-testing guard: record how many (angle, window) patterns were tested for this company. If the candidate would not pass at a stricter threshold scaled by that count (Bonferroni-style: require deviation >= 1.5 + 0.25 * log2(patterns_tested)), downgrade to Weak.

Failing a check sets state to `rejected` (logged in the rejected-findings log) or `no_reliable_finding`.

### 5.5 Evidence score (0 to 100)

```
score = 25*persistence_norm        # min(persistence/6, 1)
      + 20*magnitude_norm          # min(|gap| / (3*spread), 1)
      + 20*peer_adjusted_norm      # min(peer_adjusted_deviation / 4, 1)
      + 20*independent_sources_norm# min(distinct_source_layers/3, 1)
      + 15*robustness_norm         # share of alternative explanations resisted
label  = Strong   if score >= 70 and layers >= 3 and persistence >= 4
         Moderate if score >= 45 and layers >= 2
         Weak     otherwise
```

Business importance (size of the issue) is stored separately and NEVER feeds the label.

### 5.6 Skeptic budget

At least 30 percent of search queries issued for a candidate must be tagged `disconfirming` (looking for evidence against). Each query is tagged by the hypothesis agent. Metric M16 measures this.

---

## 6. Metrics registry (source of truth: `config/metrics.yaml`)

Create this file exactly. `make eval` reads it and prints a tiered scoreboard.

```yaml
# direction: higher_better | lower_better | band
# lower  = worst acceptable (floor). target = plan. stretch = upper bound (beyond is best).
metrics:
  # ---- correctness ----
  - id: M01_reconciliation_rate
    what: computed figures matching published figures within max(0.5% of value, 1 rounding unit)
    unit: percent
    direction: higher_better
    lower: 90
    target: 95
    stretch: 99
    measure: eval/reconcile.py over >=4 companies x >=6 periods x every computed metric

  - id: M02_claim_grounding_rate
    what: dossier claims with a live source URL, page and a cached snippet that contains the value
    unit: percent
    direction: higher_better
    lower: 90
    target: 97
    stretch: 100
    measure: eval/grounding.py re-opens each cached source and string-matches the snippet

  - id: M03_unsupported_claims
    what: claims in dossiers with no ledger entry
    unit: count
    direction: lower_better
    lower: 0
    target: 0
    stretch: 0
    gate: true
    measure: eval/grounding.py

  - id: M04_llm_authored_numbers
    what: numeric tokens in a dossier that are not inserted from the ledger
    unit: count
    direction: lower_better
    lower: 0
    target: 0
    stretch: 0
    gate: true
    measure: tests/test_numbers_from_ledger.py

  - id: M14_determinism
    what: numeric outputs identical across two reruns from cache
    unit: percent
    direction: higher_better
    lower: 100
    target: 100
    stretch: 100
    gate: true
    measure: eval/rerun_check.py

  # ---- generality and honesty ----
  - id: M05_companies_end_to_end
    what: companies completed end to end with zero code changes (Track C NIFTY 50 plus other listed sector peers)
    unit: count
    direction: higher_better
    lower: 4
    target: 6
    stretch: 9
    measure: eval/run_all.py (verify the NIFTY 50 Track C list at build time)

  - id: M06_abstain_correctness
    what: planted missing-data cases where the system abstains instead of inventing a value
    unit: percent
    direction: higher_better
    lower: 95
    target: 100
    stretch: 100
    measure: eval/canary/missing_data.py

  # ---- discovery power (canary lab) ----
  - id: M07_canary_recall
    what: planted anomalies detected, correct type, gap start within +-1 period
    unit: percent
    direction: higher_better
    lower: 70
    target: 85
    stretch: 95
    measure: eval/canary/run.py on synthetic panels

  - id: M08_canary_false_positive_rate
    what: clean synthetic companies that wrongly produce a published finding
    unit: percent
    direction: lower_better
    lower: 20
    target: 10
    stretch: 5
    measure: eval/canary/run.py

  - id: M09_gap_start_error
    what: median absolute error of detected gap start period on planted anomalies
    unit: periods
    direction: lower_better
    lower: 1.0
    target: 0.5
    stretch: 0
    measure: eval/canary/run.py

  - id: M13_window_stability
    what: same verdict class when the expected range is built from 3 different history windows
    unit: percent
    direction: higher_better
    lower: 60
    target: 80
    stretch: 95
    measure: eval/stability.py

  # ---- self-challenge ----
  - id: M10_redteam_rejection_band
    what: share of candidate gaps rejected by red-team or gate. Not a goal. Sanity band only.
    unit: percent
    direction: band
    band: [20, 80]
    note: near 0 means the red-team is toothless, near 100 means the detector is too noisy
    measure: eval/run_all.py

  - id: M16_disconfirming_query_share
    what: share of search queries tagged as looking for evidence against the hypothesis
    unit: percent
    direction: higher_better
    lower: 20
    target: 30
    stretch: 40
    measure: logs/queries.jsonl

  # ---- versus existing approaches ----
  - id: M11_baseline_advantage
    what: mean (ARGUS composite minus best baseline composite) on a 0-6 blind rubric, per company
    unit: rubric_points
    direction: higher_better
    lower: 0.5
    target: 1.5
    stretch: 2.5
    measure: eval/baselines/score.py (>=4 companies, blind reviewer who did not build the system)

  - id: M12_strong_label_precision
    what: findings labelled Strong that the blind reviewer agrees are real and supported
    unit: percent
    direction: higher_better
    lower: 80
    target: 90
    stretch: 100
    measure: eval/baselines/score.py (report the count, expect small n)

  # ---- practicality ----
  - id: M15_live_latency_seconds
    what: wall-clock seconds from company input to dossier, with cached sources
    unit: seconds
    direction: lower_better
    lower: 600
    target: 240
    stretch: 120
    measure: eval/run_all.py

  - id: M17_cost_per_run_usd
    what: model API cost per company run
    unit: usd
    direction: lower_better
    lower: 3.0
    target: 1.0
    stretch: 0.5
    measure: logs/usage.jsonl

  # ---- optional stretch ----
  - id: M18_hindsight_persistence
    what: gaps flagged using only data available 2+ years ago that were still present in the following 2 periods
    unit: percent
    direction: higher_better
    lower: 50
    target: 65
    stretch: 80
    optional: true
    measure: eval/hindsight.py (as-of cutoff on cached data, report n)
```

Scoreboard output format (`eval/results/scoreboard.md`):

```
ID                          value   lower  target  stretch  tier
M01_reconciliation_rate     96.2    90     95      99       TARGET
M08_canary_false_positive   7.0     20     10      5        TARGET
M07_canary_recall           96.0    70     85      95       BEYOND
```

---

## 7. Development plan (task list)

Priority: P0 must exist, P1 should exist, P2 only if P0 and P1 are green.
If time runs short, cut in this order: T24, T23, T22, T19, T18. Never cut T03, T04, T07, T09, T14, T17.

### Day 0 and 1: Sun 18 and Mon 19 Oct

- **T01 (P0)** Repo skeleton, `pyproject.toml`, `Makefile` (`make test`, `make eval`, `make run COMPANY=...`), `config/metrics.yaml`, empty modules. Acceptance: `make test` runs and passes with a placeholder test.
- **T02 (P0)** `schemas.py` from Section 4 and `ledger.py` (append, lookup, hash check). Acceptance: round-trip test; changing a cached file breaks the hash check.
- **T03 (P0)** `tests/test_no_hardcoding.py` for rule R1 and `tests/test_numbers_from_ledger.py` for R2 and R3. Acceptance: tests fail on a deliberate violation, pass on clean code. Moves M03, M04.
- **T04 (P0)** Canary lab: `eval/canary/generate.py` makes synthetic company panels (40 companies, 8 half-year periods): 20 clean, 20 with ONE planted anomaly among `price_led_growth`, `receivable_stretch`, `inventory_build`, `combined`, with seeded noise. Ground truth file records type and true start period. Acceptance: deterministic output for a given seed; ground truth file validates. This is the main source of hard numbers because it needs no labelled real data.
- **T05 (P1)** Ingestion smoke test: fetch results and annual report notes for 2 Track C companies from exchange or company investor pages, cache with hashes. Verify any library (for example `nselib`) with a real call before relying on it. Fallback: download PDFs or XBRL directly. Acceptance: files cached, hashes stored.
- Round 1 report submitted by Mon 19 Oct, 6 PM IST (buffer before the 11:59 PM deadline).

### Day 2: Tue 20 Oct

- **T06 (P0)** `ingest/pdf_tables.py`: extract receivables, inventory, revenue, volume growth, cash flow into ledger entries with page and snippet. Acceptance: ledger entries exist for 2 companies x 6 periods where disclosed; missing items are marked absent, not zero.
- **T07 (P0)** Angle modules (`angles/price_volume.py`, `working_capital.py`, `cash_conversion.py`) per 5.1, each with abstain logic. Acceptance: unit tests on hand-computed examples. Moves M01, M06.
- **T08 (P0)** `eval/reconcile.py`: recompute metrics and compare with published figures. Acceptance: prints M01 with counts.

### Day 3: Wed 21 Oct

- **T09 (P0)** `baseline_range.py` and `residual.py` per 5.2. Acceptance: on canary data, M07 at or above FLOOR and M08 at or below FLOOR.
- **T10 (P1)** `peers.py`: pick 3 to 5 peers by business-model profile (not by hard-coded names), compute peer gaps, peer-adjusted deviation. Acceptance: sector-wide planted gap is labelled "sector story".
- **T11 (P1)** `angles/cross_metric.py` per 5.3. Acceptance: a planted `combined` anomaly is found as one candidate. Moves M07, M09.
- **T12 (P0)** `eval/canary/run.py` produces M07, M08, M09, M06 and writes `eval/results`.

### Day 4: Thu 22 Oct

- **T13 (P0)** `llm.py` adapter (one function `complete(prompt, model_tier)`, vendor-agnostic, with usage logging) and `profile.py` (classify distributor-led, own-store retail, diversified). Acceptance: profile decides which angles run; a retailer without distributors skips distributor metrics with a logged reason.
- **T14 (P0)** `agents/hypothesis.py` (research and analysis capabilities: plan searches, tag each query `supporting` or `disconfirming`, read sources, propose causes with NO numbers) and `agents/redteam.py` (seasonality, accounting changes, pricing lag, sector-wide). Acceptance: query log shows tags; M16 computed.
- **T15 (P0)** `validation_gate.py` per 5.4. Acceptance: unit tests for each of the five checks; rejected candidates go to the log.
- **T16 (P0)** First end-to-end run on 1 company, then 2 more with zero code changes. Acceptance: M05 at least 3 so far.

### Day 5: Fri 23 Oct (results announced)

- **T17 (P0)** `verify/claim_checker.py` and `verify/score.py` (5.5) and `report/dossier.py` with all eight required output items. Acceptance: M02, M03, M04 green; every dossier validates against the schema.
- **T18 (P1)** Baselines: `eval/baselines/ratio_screen.py` (flags any metric whose year-on-year change exceeds a fixed threshold) and `eval/baselines/plain_llm.py` (one prompt, same filings, no tools, asks for a non-obvious insight). Rubric in `eval/baselines/rubric.md`: Real (0 to 2, numbers reconcile), Non-obvious (0 to 2, not stated by management and not visible from a headline ratio), Supported (0 to 2, at least 2 independent sources with working links). Outputs are shuffled and anonymised before the blind reviewer scores them. Acceptance: M11, M12 computable.
- **T19 (P1)** `eval/stability.py` (M13) and `eval/rerun_check.py` (M14).

### Day 6: Sat 24 Oct (hardening day, code freeze 6 PM IST)

- **T20 (P0)** Cache sources for 6 or more Track C companies plus 2 or 3 non-distributor or out-of-index peers. Acceptance: a cold run works with the network off.
- **T21 (P0)** Streamlit dashboard `app/streamlit_app.py`: discovery card with why-it-matters, key numbers, residual chart (expected band, reported line, peers), timeline, clickable evidence trail, red-team log, falsification panel, evidence score with its five inputs. Acceptance: all eight required items visible and every claim clickable.
- **T22 (P2)** **Proof Panel**: a dashboard tab that shows the live scoreboard (Section 6 tiers) and a side-by-side of ARGUS versus the ratio screen versus the plain LLM summary on the same company, so judges can compare on screen. Acceptance: renders from `eval/results` with no hand-typed numbers.
- **T23 (P2)** **Living findings**: `eval/falsification_watch.py` re-checks each stored falsification condition against newer cached data and shows "holds / overturned / not yet testable".
- **T24 (P2)** `eval/hindsight.py` (M18).
- **T25 (P0)** Latency and cost pass (stream the agent trace to the UI, parallelise fetches), then `make eval` full run. Acceptance: M15 and M17 at or above FLOOR.
- **T26 (P0)** Backup demo video (under 2 minutes) and a rehearsed 10-minute talk. Freeze code at 6 PM.

### Day 7: Sun 25 Oct (finals)

No new features. Morning: run `make test`, run one cold smoke test, confirm cached data. Demo on the company the judges pick. If the agent abstains, say so and show the not-tested list: that is a feature.

---

## 8. Solo or small-team fallback

- If fewer than 3 people: use the sequential pipeline, skip T22 to T24, and do T18 with only the ratio screen plus the plain LLM on 3 companies.
- Minimum credible demo: price versus volume plus receivable days with source links, the red-team log, the evidence score, an abstain case, and canary lab numbers.

---

## 9. What makes this different (talking points, keep them true)

1. **Residual-first**: the numbers choose what gets researched.
2. **Canary Lab**: planted anomalies in synthetic data give measurable recall and false-positive rates without needing labelled real data.
3. **Proof-carrying numbers**: every figure has URL, page, snippet and file hash, and the checker re-opens the source.
4. **Skeptic budget**: a minimum share of searches must look for evidence against our own hypothesis.
5. **Abstention as a scored feature**, not a failure.
6. **Living findings**: each falsification condition is stored and re-checked against newer data.

Claim only what `make eval` actually measured.

---

## 10. Definition of done

- All gate metrics (M03, M04, M14) satisfied.
- Every non-optional metric at FLOOR or better; as many as possible at TARGET; any at BEYOND is a bonus.
- Cold run works offline from cache on at least 6 companies.
- Dashboard shows all eight required output items with clickable evidence.
- Scoreboard file generated by `make eval` is what we quote on stage.
