# ARGUS-Consumer: Team Handoff and What Remains

**Project status last checked: October 21, 2026**

## What ARGUS does

ARGUS helps a reviewer look for unusual patterns in a consumer company's public financial reports. A person chooses a company and a public report. The system can cache the PDF, record its SHA-256 fingerprint, and extract possible financial claims. Those claims are only suggestions until a person checks the cited PDF page and approves them. Approved observations are stored with their source, period, units, reporting basis, scope, and review details.

The analysis engine then compares compatible observations across time and peers. Its calculations and detection rules are deterministic Python code. It abstains when information is missing, ambiguous, or out of scope. The optional LLM can help with language-based research and locating likely evidence, but it must not create financial numbers, approve evidence, or decide that an anomaly is real.

ARGUS is a working research prototype. It is not yet a validated discovery system, and it does not provide investment advice.

## What is working now

- Online company intake can search public sources, cache a selected PDF, and prepare claims for review. Cached reports and approved ledger data can also be analyzed without fetching new material.
- The evidence ledger records reviewed observations with source URLs, cached-file hashes, page references, snippets, periods, units, and reporting metadata.
- The analysis engine builds historical and peer panels, keeps different reporting scopes separate, and preserves missing data instead of filling gaps with zeroes.
- The dashboard presents the company dossier, analysis, evidence trail, abstentions, and audit export.
- Six companies have verified data in the current ledger: Hindustan Unilever Limited (30 observations), ITC Limited (38), Britannia Industries Limited (18), Marico Limited (24), Dabur India Limited (18), and Godrej Consumer Products Limited (18).
- The last recorded regression run passed **52 tests**. The last dashboard checks recorded **0 AppTest exceptions** and an HTTP 200 health response. These checks were last recorded on October 21; the team should repeat them before submission if code changes.

## What the current results mean

All six company runs returned `no_reliable_finding`, with zero generated candidates and zero rejected candidates. This means no company passed the current discovery gates. It does **not** prove that no business issue exists.

HUL had one flagged receivables period and ITC had one flagged period for each of two metrics. The existing persistence rule requires three consecutive periods, so those flags did not become candidates. GCPL's history is split around its Raymond Consumer Care acquisition: four pre-acquisition periods and two post-acquisition periods. Neither group is long enough for the six-period history rule. No detection threshold was changed.

M01, the real-company reconciliation measure, is still **unavailable: 0 matched out of 0 compared**. Four GCPL published ratios have been checked and retained in [`config/reconciliation.yaml`](config/reconciliation.yaml), but they use average balances and net sales and report turnover ratios. ARGUS's current days calculations use closing balances and revenue from operations. The formulas differ, so the evaluator excludes those references. A recent LLM-assisted search did not find an exact formula for Dabur in the reviewed excerpts. Dabur's report lists “days of sales” values without stating a clear calculation formula or basis; those values remain unresolved. See the [M01 formula search notes](reports/m01-formula-discovery.md).

Other recorded scores also have limits. The measured missing-data and anomaly-detection scores are from synthetic cases, not real companies. Real blind-review accuracy, real red-team outcomes, and comparable revenue-matched volume data have not been measured. The current synthetic results and full company-by-company details are in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) and [`config/metrics.yaml`](config/metrics.yaml).

## What team members need to do manually

The following work requires people to review company reports and make evidence decisions. The LLM and PDF extractor can help locate passages, but neither can verify a value or settle a comparability question.

1. **Choose the companies and periods to cover.** Use the approved Track C company list and agree on the fiscal periods and reporting basis to compare. Keep standalone and consolidated data separate. Mark acquisitions, demergers, discontinued operations, and other changes in scope.
2. **Find the official source for each company.** Prefer the company's investor-relations site or an official BSE, NSE, or SEBI filing. Save or select the report in the dashboard's online intake. Search snippets and third-party summaries are leads only.
3. **Review every proposed financial claim in the PDF.** Open the cited page and check the exact printed value, unit, fiscal period, standalone/consolidated basis, and reporting scope. Confirm the table headers and comparative-year columns. Record the exact page and source wording. If any field is unclear or sources conflict, leave the claim unresolved; do not guess or enter zero.
4. **Approve only claims you have checked.** Use the dashboard's review flow to approve verified observations. Make sure each approved row retains its source URL, cached SHA-256, page or locator, snippet, reviewer, and review status. Keep unreviewed extraction candidates out of the verified ledger.
5. **Build the M01 comparison set.** In each report, look for a formula note that exactly matches the metric ARGUS calculates, including the balance definition, denominator, number of days, period, basis, and scope. The planned M01 breadth is at least four companies and six comparable periods per company, covering every metric being tested. Write down both eligible matches and excluded references with the reason. Do not convert turnover ratios, average balances, COGS, or net-sales formulas into a different metric and call them matches.
6. **Collect volume data only when it truly matches revenue.** Check that volume growth and revenue growth cover the same company or segment, geography, period, and definition. Do not pair underlying growth with reported revenue unless the adjustments and scope are shown to match.
7. **Arrange independent human review.** Have a reviewer who did not prepare the analysis score anonymized ARGUS and baseline results using [`eval/baselines/rubric.md`](eval/baselines/rubric.md). Record the number of cases, reviewer, scores, and uncertainty. Keep the system identities hidden until scoring is complete.
8. **Challenge real candidates if any pass the gates.** For each persistent candidate, have a separate reviewer look for alternative explanations such as seasonality, acquisitions, accounting changes, and sector-wide movements. Save the supporting or disconfirming source and the reviewer's decision. If there is no qualifying candidate, record the red-team result as “not tested”; do not create an example finding.

## Final checks before calling the project complete

The team should be able to show a reviewer the original source for every approved observation; explain every unmatched or abstained period; meet the configured M01 breadth and accuracy floor with source-traceable comparisons; and report real human-review results separately from synthetic scores. The dashboard and test suite should be checked again after the final data or code changes. Use the existing rules in [`config/metrics.yaml`](config/metrics.yaml); do not lower thresholds to force a result.

Only call something a real discovery if it clears the existing validation gate and every supporting claim can be traced back to reviewed source evidence. Until then, an honest abstention is the correct output.
