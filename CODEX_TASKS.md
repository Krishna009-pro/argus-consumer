# ARGUS-Consumer: Codex Improvement Tasks & Upgrades

This document is a direct, sequential execution guide for **Codex** (or any coding agent) to improve ARGUS, eliminate current bottlenecks, and transition the prototype from an abstention state to a validated finding.

---

## 0. Hard Rules (Must Obey at All Times)

Before modifying any file, verify strict compliance with the core project rules:
- **R1:** No company-specific code or heuristics in `src/` logic. (`tests/test_no_hardcoding.py` must pass).
- **R2:** Every number in outputs must map to a valid ledger ID (`L0001`, `L0002`, etc.).
- **R3:** LLMs must never author or compute numbers. All calculations are pure Python.
- **R4:** Missing input means **ABSTAIN** for that angle. Never guess, interpolate, or substitute zeros.
- **R5:** Findings require $\ge 2$ independent source layers. "Strong" requires $\ge 3$.
- **R6:** Public data only. Offline cache with SHA-256 validation.
- **R7:** Objective factual framing only. No investment recommendations or accusations.
- **R8:** Content-addressed caching (`data/cache/<sha256>.<ext>`) with tamper verification.

---

## Task 1 (P0): Fix Multi-Panel Aggregation Bias in `engine.py`

### Problem
In `src/argus/engine.py` (lines 103–108), `make_dossier()` extracts candidates, strong signals, score components, and red-team logs **only from the last panel** (`latest = rows[-1]`). If an earlier panel (such as the 6-year FY2020–FY2025 panel) produces candidates, but the final 1-year panel does not, the candidate is dropped from the final dossier headline.

### Instructions for Codex
1. In `src/argus/engine.py`, update `make_dossier()`:
   - Collect `all_candidates = [c for r in rows for c in r["candidates"]]`.
   - Collect `strong = [c for c in all_candidates if c["state"] == "unexplained"]`.
   - If `strong` exists, pick the highest-scoring candidate (or first strong candidate) and calculate the evidence score from its supporting panel.
   - Aggregate `all_peer_companies = list(dict.fromkeys(c for r in rows for c in r.get("peer_companies", [])))`.
   - Aggregate all red-team logs across all panels in `rows`.
2. Ensure `dossier.discovery` accurately reflects if an anomaly was detected across *any* panel.
3. Write a unit test in `tests/test_panels.py` or `tests/test_peers.py` verifying that a candidate generated in panel 0 is retained in the final dossier even if panel 1 has no candidates.

**Acceptance Line:** `python scripts/run_tests.py` passes with the new multi-panel test.

---

## Task 2 (P0): Standardize Numeric Evidence Keys in `engine.py`

### Problem
In `src/argus/engine.py` (line 130), numeric claim keys are formatted as:
```python
numbers[f"{angle_name} {period} inputs {','.join(ids)}"] = val
```
However, `tests/test_numbers_from_ledger.py` requires numeric keys to contain ledger IDs enclosed in brackets matching the regex `r"\[L\d{4}\]"`.

### Instructions for Codex
1. In `src/argus/engine.py` (line 130), change the dictionary key formatting to:
```python
numbers[f"{angle_name} {period} [{', '.join(ids)}]"] = val
```
2. In `src/argus/engine.py` (line 70), protect against empty `ledger_ids_by_period`:
```python
ids_by_period = angle.get("ledger_ids_by_period", [])
ids = ids_by_period[latest] if latest < len(ids_by_period) else []
```

**Acceptance Line:** `python scripts/run_tests.py` passes.

---

## Task 3 (P1): Upgrade PDF Table Extraction with `pdfplumber`

### Problem
`src/argus/ingest/pdf_tables.py` uses basic single-line regex on raw text extracted via `pypdf`. In complex Indian annual report statements, note reference columns (e.g. Note 11, Note 12, Note 25) sit adjacent to line items and get falsely extracted as financial values, producing noisy unverified proposals.

### Instructions for Codex
1. `pdfplumber>=0.11` is already in `pyproject.toml` under `[project.optional-dependencies.ingest]`.
2. Refactor `src/argus/ingest/pdf_tables.py` to use `pdfplumber.open(path)`:
   - Use `page.extract_tables()` to detect grid boundaries.
   - Separate row descriptions, note reference numbers, and financial figure columns.
   - Explicitly ignore numeric tokens found inside "Note" or "Schedule" columns.
   - Only propose numbers from columns headed by financial years (e.g., `2026`, `2025`, `FY26`).
3. Add a test in `tests/test_claim_checker.py` ensuring note references (like Note 11) are rejected as candidate values.

**Acceptance Line:** Extracting candidates from `data/cache/98219f80b28472d4d11c893274e0537b5098c98f34dcc30c7f905db3cb7a929b.pdf` yields 0 note-reference candidates.

---

## Task 4 (P1): Ingest Peer Company Panels (ITC Limited)

### Problem
`validation_gate.py` requires `peer_adjusted_deviation >= 1.5`, which in turn requires at least 3 peer data points in `metrics.py: peer_adjusted_deviation()`. Currently, there are 0 peer observations in `data/ledger.jsonl`. Without peers, HUL's FY2025 receivables spike cannot clear the validation gate.

### Instructions for Codex
1. Download official BSE/NSE annual reports for **ITC Limited** covering FY2020 through FY2025.
2. Cache them in `data/cache/` with their SHA-256 hashes.
3. Use `python scripts/argus.py record` to add verified standalone:
   - `revenue` (FY2020–FY2025)
   - `trade_receivables` (FY2020–FY2025)
   - `inventory` (FY2020–FY2025)
   with physical PDF pages, exact statement snippets, and reviewer notes.
4. Verify that running `python scripts/argus.py run --company "Hindustan Unilever Limited"` now detects ITC Limited as an eligible peer panel in `eligible_peer_panels()`.

**Acceptance Line:** `reports/hindustan-unilever-limited-analysis.json` lists `peer_companies: ["ITC Limited"]`.

---

## Task 5 (P2): Structured Red-Team Decision Model (Jev / Instructor)

### Problem
In `src/argus/agents/redteam.py`, all 7 benign checks (`seasonality`, `base_effects`, `one_off_events`, `accounting_changes`, `acquisitions_or_demergers`, `pricing_lags`, `sector_wide_movements`) currently return `not_tested` because qualitative text analysis is not connected.

### Instructions for Codex
1. Integrate a structured decision model (such as **Jev** by TypeSafe AI, or **Instructor** with Pydantic):
   - Jev provides single-pass (70–500ms), non-generative, typed schema decisions (`is_demerger_related: bool`, `confidence: float`).
   - If using Groq/OpenRouter, wrap the call with `instructor` to enforce strict schema adherence without prose or free-form digits.
2. In `src/argus/agents/redteam.py`:
   - Feed relevant report note snippets (e.g. Note 44 on the Ice Cream demerger) into the decision model.
   - Populate `outcome: "passed" | "rejected" | "benign_alternative_confirmed"` and compute `benign_gap_share`.
3. Ensure no numeric tokens are authored by the model; only schema-constrained categories and probabilities.

**Acceptance Line:** `dossier.red_team_log` contains tested outcomes rather than `not_tested`.

---

## Task 6 (P2): Add Volume Growth for FMCG Price/Volume Discovery

### Problem
`price_volume` angle is currently abstaining across all panels because `volume_growth` is absent from the ledger. In consumer goods, price-led revenue growth masking volume contraction is a premier discovery.

### Instructions for Codex
1. Locate HUL's reported underlying domestic consumer volume growth in official quarterly/annual presentations for FY2021–FY2025.
2. Record `volume_growth` entries into `data/ledger.jsonl` with units `percent`.
3. Re-run `python scripts/argus.py run --company "Hindustan Unilever Limited"`.
4. Verify that the `price_volume` angle produces a tested series.

**Acceptance Line:** In `reports/hindustan-unilever-limited-analysis.json`, `angles.price_volume.status` changes to `"tested"`.

---

## Task 7: Full Evaluation & Health Run

After completing the tasks above:
1. Run test suite:
   ```powershell
   python scripts/run_tests.py
   ```
2. Run full evaluation:
   ```powershell
   python scripts/argus.py eval
   ```
3. Generate updated company dossier:
   ```powershell
   python scripts/argus.py run --company "Hindustan Unilever Limited"
   python scripts/argus.py export-pdf --company "Hindustan Unilever Limited"
   ```
4. Verify Streamlit dashboard renders the new panels, proof comparisons, and peer charts:
   ```powershell
   streamlit run app/streamlit_app.py
   ```
