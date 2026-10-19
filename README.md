# ARGUS-Consumer

ARGUS is a public-data financial discovery prototype. Ordinary Python computes metrics; an optional language model can help plan qualitative research, but it cannot supply or edit numerical results. Every recorded source observation is tied to a cached file, SHA-256, URL, period and exact snippet. Missing evidence produces an abstention.

## Setup

Use Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -e ".[dashboard,ingest]"
```

`dashboard` and `ingest` are optional extras. Core calculations and synthetic evaluation work without them. The PDF extractor requires `ingest`; the PDF dossier export requires `dashboard`.

## Commands

With GNU Make installed:

```text
make test
make eval
make run COMPANY="Company name"
```

On Windows without GNU Make, use `make.bat test`, `make.bat eval`, or:

```powershell
$env:COMPANY = "Company name"
make.bat run
```

Or invoke the CLI directly with `python scripts/argus.py eval`, `python scripts/argus.py run --company "Company name"`, and `python scripts/argus.py export-pdf --company "Company name"`.

## Public sources and offline cache

Fetch an official public source (exchange/company investor page) with:

```text
python scripts/argus.py cache https://public.example/annual-report.pdf
```

The command stores the response content-addressed under `data/cache/` and prints its SHA-256. Add a disclosed value only after checking the page, period, units and exact snippet:

```text
python scripts/argus.py record --company "Company name" --metric revenue --value 1250 --unit INR_cr --period FY26 --period-type annual --currency INR --basis consolidated --verified-by "Reviewer name" --source-url https://public.example/report.pdf --source-type filing --snippet "Revenue from operations 1,250" --cache-path data/cache/<sha>.pdf --page 42
```

The record command requires reviewer metadata and the same period/currency/basis fields, and rejects snippets that are not present on the specified cached PDF page. Optional `--reporting-scope`, `--comparability-cohort`, and `--comparability-note` fields preserve scope breaks. PDF verification uses `pypdf`. The PDF candidate extractor only proposes supported line items on pages with dated financial-statement headers and selects the rightmost dated value columns, avoiding numeric Note references; it still requires a person to verify the row, column, unit and reporting basis. Candidate IDs are content-based so reordered extraction does not overwrite prior review history. Copy `data/cache/` and `data/ledger.jsonl` to reproduce ledger checks offline. Do not enter estimates, unpublished inputs or values whose table alignment is uncertain. Machine-extracted PDF candidates are deliberately flagged for review.

Verified observations are assembled into panels by company, period type, currency, and consolidation basis. Formula outputs retain their ledger IDs and abstain when inputs, units, period duration, or compatible peers are missing. A finding also requires passing persistence, peer, source-integrity, alternative-explanation, multiple-testing, and independent-source gates. A single reviewed value is insufficient.

### Import locally obtained public filings

If the official host blocks automated download, save its public PDF under `data/incoming/` and register it as unverified candidates. For the HUL FY 2025–26 report, create the input directory in PowerShell and use the browser's Save As dialog to save the supplied official link as `data/incoming/hul-annual-report-2025-26.pdf`:

```powershell
New-Item -ItemType Directory -Force .\data\incoming | Out-Null
python scripts/argus.py import-local .\data\incoming\hul-annual-report-2025-26.pdf --company "Hindustan Unilever Limited" --source-url https://www.hul.co.in/files/annual-report-2025-26.pdf
$candidateFile = Get-ChildItem .\data\candidates\candidates-*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$candidates = Get-Content $candidateFile.FullName -Raw | ConvertFrom-Json
$candidates | Format-Table id,metric,value,unit,period,doc_page,status,snippet -Wrap
```

For each proposed row, open the same PDF, locate the printed table and page, and confirm the figure, row/column heading, unit, financial period and statement basis (consolidated or standalone). The importer labels proposals `unverified`; it does not decide those fields. Approve only a value that matches the source. Substitute the candidate ID and the reviewed metadata below with what the report actually says:

```powershell
$candidateId = Read-Host "Candidate ID from the table above"
$reviewer = Read-Host "Reviewer name"
$period = Read-Host "Exact period label checked in the report"
$unit = Read-Host "Unit checked in the report"
$currency = Read-Host "Currency code, or N/A for a non-currency metric"
$basis = Read-Host "Statement basis: consolidated, standalone, or unknown"
python scripts/argus.py verify-candidate $candidateFile.FullName $candidateId --verified-by $reviewer --period $period --unit $unit --period-type annual --currency $currency --basis $basis
```

Repeat for each approved observation. Leave missing, ambiguous, or conflicting rows unapproved. Add `--period-start YYYY-MM-DD --period-end YYYY-MM-DD` only when those exact dates are established from the report. The `verify-candidate` command retains the cached file hash, source URL, extractor page/snippet, and reviewer/time in the ledger. If the extracted number itself is wrong but you can verify the correct number from a literal source snippet, use the documented `record` command with that corrected value and the PDF page. Streamlit currently displays dossiers and evidence; it does not import PDFs or approve candidates.

For a structured observation CSV, include `metric,value,unit,period,snippet`; optional columns are `period_type,period_start,period_end,currency,consolidation_basis,page`. The source snippet must occur literally in the CSV. The source document remains the authoritative basis of review. Neither importer writes verified observations.

Review a candidate against the original official source, then approve it into the append-only ledger:

```powershell
python scripts/argus.py verify-candidate data/candidates/candidates-<hash>.json <candidate-id> --verified-by "Reviewer name" --period FY26 --unit INR_cr --period-type annual --currency INR --basis consolidated --period-start 2025-04-01 --period-end 2026-03-31
```

Enter the source's actual period labels, units, currency, statement basis and page. Use `unknown` when basis cannot be confirmed; such data will not enter peer comparisons. `record` is also available for manually transcribed values. `config/companies.yaml` is a source directory, not proof that a report was retrieved or analyzed.

### Discover and prepare a public report online

You do not need to save a report manually first. With `SERPER_API_KEY` configured, run:

```powershell
python scripts/argus.py prepare-company --company "Company Name"
```

ARGUS searches public web results, selects the highest-ranked result whose title says “annual report” and whose URL ends in `.pdf`, downloads it into the content-addressed cache, and writes page-linked extraction candidates. This source selection is still unverified. If the result list is ambiguous, the command returns choices without downloading; choose a result explicitly or pass the official URL:

```powershell
python scripts/argus.py prepare-company --company "Company Name" --result 2
python scripts/argus.py prepare-company --company "Company Name" --url "https://official.example/annual-report.pdf"
```

The command never approves observations. Inspect each selected PDF page and candidate context, then use `verify-candidate` only for a matching value with confirmed period, unit, basis and scope. Search results, automatic source selection and extracted values remain unverified; deterministic analysis reads only reviewed ledger entries with intact source hashes.

## Optional model configuration

No credentials are required for deterministic analysis. To enable the optional model adapter, add provider credentials and select a provider in the project-root `.env`:

```text
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
ARGUS_LLM_PROVIDER=openrouter
ARGUS_LLM_MODEL=<model id supported by the selected provider>
```

Set `ARGUS_LLM_PROVIDER` to `openrouter` or `groq` and put that provider's key in the corresponding variable. Only one provider is active per request. For another OpenAI-compatible provider, set `ARGUS_LLM_BASE_URL` and `ARGUS_LLM_API_KEY` instead. The local `.env` is ignored by Git and is loaded at runtime; process environment values take precedence. The adapter logs token/cost fields only when returned by the provider; it never logs keys. Providers that do not expose a cost field report cost as unavailable.

## Optional web source discovery

ARGUS can use Serper to suggest public source URLs. These results are discovery leads only: they are not downloaded, treated as observations, or approved into the evidence ledger. Put the key in a project-root `.env` file (already ignored by Git):

```text
SERPER_API_KEY=your_key_here
```

ARGUS loads this file for source discovery, without overriding a key already set in the process environment. Then run:

```powershell
python scripts/argus.py search-web --query "Hindustan Unilever annual report FY 2025-26" --limit 10
```

The key is read only from the process environment and must never be committed to source control. Serper is optional; local PDF import and deterministic analysis remain available without it.

## Dashboard

Install the optional dashboard extra, run at least one company command, then start:

```text
streamlit run app/streamlit_app.py
```

The dashboard shows generated dossiers, verified panels, exact abstention reasons, the existing ratio-screen comparison, and source evidence. It does not upload or approve PDFs. No placeholder companies or fabricated company metrics are bundled. Evaluation scoreboard entries distinguish measured synthetic results from unavailable human or real-world measurements. PDF export is available in the dashboard or through `export-pdf`.

## Evaluation and limitations

`make eval` runs seeded synthetic canaries, missing-input abstention checks, deterministic reruns and stability checks, then writes `eval/results/summary.json` and `eval/results/scoreboard.md`. Canary metrics are explicitly synthetic. Published-figure reconciliation, real-company breadth, blind baseline scores and live API cost remain unavailable until suitable verified source panels, reviewer scores and configured model telemetry exist. Scoreboard bounds are goals, never measured outcomes.

No investment recommendation or misconduct inference is produced. This prototype does not yet meet the plan's definition of done: it lacks a real multi-company financial input corpus and a fully automated filing-to-panel reconciliation pipeline. An abstention is expected until those source gaps are filled.
