# ARGUS-Consumer

ARGUS helps a reviewer look for unusual patterns in a consumer company's public financial reports. It collects source documents, proposes figures for review, and compares only the observations a person has checked against the original report.

The regular analysis command uses Python for its calculations; it does not call an LLM. The project also has a separate, optional hypothesis agent for qualitative research. It cannot create or change financial numbers, and it was not used in the saved HUL analysis. When data is missing, unclear, or not comparable, ARGUS leaves the question unanswered. That is why an analysis can finish with **No Reliable Finding**.

ARGUS is a research prototype. It does not make investment recommendations or establish misconduct.

## How it works

1. Search for a company's public report or provide an official report URL.
2. Cache the report and record its SHA-256 fingerprint, so later checks use the same file.
3. Extract possible financial claims. These are **candidates**, not verified facts.
4. A reviewer checks each candidate against the cited PDF page, including its value, period, unit, statement basis, and reporting scope.
5. Only approved observations enter the evidence ledger and can be used in the analysis.
6. The deterministic engine compares compatible periods and applies the project's existing validation gates. It reports a candidate only when the evidence passes those gates; otherwise it explains why it abstained.

Missing values stay missing. ARGUS does not fill gaps with zeroes or estimates.

## Current project status

The latest recorded company runs cover Hindustan Unilever Limited (HUL), ITC Limited, Britannia Industries Limited, Marico Limited, Dabur India Limited, and Godrej Consumer Products Limited (GCPL). All return `no_reliable_finding`; none is a validated discovery. GCPL has manually reviewed standalone revenue, inventory, and trade-receivable data for FY2020–FY2025. Its FY2020–FY2023 pre-acquisition panel is kept separate from FY2024–FY2025 because GCPL acquired and integrated Raymond Consumer Care's FMCG business in May 2023. GCPL's published turnover ratios have also been recorded for reconciliation review, but their average-balance/net-sales formulas differ from ARGUS's closing-balance days formulas, so M01 remains unavailable. Comparable volume data, broader Track C coverage, and real-world validation are still incomplete.

For the evidence behind those results, current evaluation measurements, and remaining work, see [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Synthetic test results are not measurements of real-world accuracy.

## Set up on Windows

You need Python 3.11 or newer. From the project folder, open PowerShell and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dashboard,ingest,dev]"
```

This installs the command-line tools, PDF import and export support, dashboard, and test dependencies. If you only need the deterministic engine, install the base package with `python -m pip install -e .` instead.

## Try the command line

Run the existing tests and synthetic evaluation with:

```powershell
python scripts/run_tests.py
python scripts/argus.py eval
```

Run a company analysis with:

```powershell
python scripts/argus.py run --company "Hindustan Unilever Limited"
```

The command reads the verified observations already in the ledger. It does not invent missing history. To export the saved dossier as a PDF:

```powershell
python scripts/argus.py export-pdf --company "Hindustan Unilever Limited"
```

The PDF is written under `reports/` by default. You can choose another destination with `--output`.

## Bring in a public report

### Search online

Online search uses Serper. Create a `.env` file in the project root and add your key:

```text
SERPER_API_KEY=your_key_here
```

Then search for a company's annual report:

```powershell
python scripts/argus.py prepare-company --company "Company Name"
```

Search results are leads, not trusted sources. Check that the selected report comes from the company or a recognized exchange. If ARGUS asks you to choose a result, rerun the command with the result number it displayed:

```powershell
python scripts/argus.py prepare-company --company "Company Name" --result 2
```

If you already have the official PDF URL, you can pass it directly. This skips web search:

```powershell
python scripts/argus.py prepare-company --company "Company Name" --url "https://official.example/annual-report.pdf"
```

ARGUS caches the selected file and prints its SHA-256 hash and candidate-file path. The extracted values remain unverified. Online search and fetching need an internet connection; without one, use a report you already saved and the local import steps below. Analysis can still use evidence already in the local ledger.

### Use a PDF already on your computer

If a company site blocks automated downloads, save its public PDF in the project's `data/incoming/` folder. Create the folder if needed, then use your browser's **Save As** option to put the report there. The exact filename is up to you; pass that filename to the importer:

```powershell
New-Item -ItemType Directory -Force .\data\incoming | Out-Null
python scripts/argus.py import-local .\data\incoming\company-report.pdf `
  --company "Company Name" `
  --source-url "https://official.example/annual-report.pdf"
```

Use the official report URL as `--source-url`, even when you saved the PDF manually. The importer stores a cached copy and prints the candidate-file path. It does not approve any figures.

## Review and approve observations

Open the candidate file named in the import output and inspect the listed PDF page in the original report. Confirm the exact number and the row and column headings, as well as the financial period, unit, standalone or consolidated basis, and reporting scope. A printed page number and a PDF viewer's page number can differ, so check the cited page in context.

To approve one candidate, substitute its actual ID and the details you confirmed:

```powershell
python scripts/argus.py verify-candidate ".\data\candidates\candidates-<hash>.json" "<candidate-id>" `
  --verified-by "Your name" `
  --period "FY2025" `
  --unit "INR_crore" `
  --period-type annual `
  --currency INR `
  --basis consolidated
```

Use the report's actual values for these fields. Choose `standalone`, `consolidated`, or `unknown` for `--basis`. If the period, unit, or figure is unclear or conflicts with another source, do not approve it. An unknown basis will not be used in peer comparisons.

If you have already manually recorded and verified the same observation, link the extracted candidate to that ledger row instead of adding a duplicate:

```powershell
python scripts/argus.py link-candidate ".\data\candidates\candidates-<hash>.json" "<candidate-id>" --ledger-entry "L0001"
```

The command requires the candidate and existing verified ledger row to match on company, metric, value, source URL, PDF page and cached-file hash; it also checks both snippets against the cached source. It marks the candidate as verified and records its ledger ID without creating a second observation.

After reviewing the candidates you need, run the company analysis again:

```powershell
python scripts/argus.py run --company "Company Name"
```

For a value you transcribed yourself, `record` is available. It still requires the cached source, page, a literal snippet from that page, and reviewer details. See `python scripts/argus.py record --help` for the required fields.

## Open a dashboard

### Python-backed dashboard

This is the dashboard to use for actual online intake and saved company reports. Start it from the project folder:

```powershell
streamlit run app/streamlit_app.py
```

In **Live company intake**, search for a company, choose a public report, then fetch the PDF. ARGUS shows the extracted candidates with their pages and snippets. Review and approve them with the CLI command above; the dashboard does not approve figures for you.

### React dashboard preview

There is also a separate visual preview under `dashboard/`. It uses bundled report snapshots and sample intake responses; its intake buttons do not search the web or fetch a live report. Use the Python-backed dashboard or CLI when you need actual source intake.

To run the preview:

```powershell
cd dashboard
npm ci
npm run dev
```

## Optional language model

You do not need an LLM key to import reports or run the deterministic analysis. The optional adapter can help with qualitative research; it must not supply, calculate, or edit financial values.

To enable it, add the key for your chosen provider and its model name to the project-root `.env` file:

```text
ARGUS_LLM_PROVIDER=openrouter
ARGUS_LLM_MODEL=your-provider-model-id
OPENROUTER_API_KEY=your_openrouter_key
```

Set `ARGUS_LLM_PROVIDER` to `openrouter` or `groq`, and use the matching key (`OPENROUTER_API_KEY` or `GROQ_API_KEY`). Keep `.env` on your computer; it is excluded from Git. Provider settings do not change the deterministic calculations.

## What is not finished

The current evidence base is too small for a reliable cross-company conclusion. In particular, ARGUS still needs more independently reviewed peer histories with matching periods and reporting scope, a comparable volume series, independent red-team evidence, and real-world validation. Its current evaluation includes synthetic cases; those results should not be presented as real-company accuracy.

Until the existing validation gates pass, treat the output as a research lead or an abstention—not as a real discovery. The project plan and [implementation status](IMPLEMENTATION_STATUS.md) describe the remaining work in more detail.

## Demo

The narrated walkthrough is available at [demo/ARGUS-Consumer-Submission-Demo.mp4](demo/ARGUS-Consumer-Submission-Demo.mp4), with a separate [subtitle file](demo/ARGUS-Consumer-Submission-Demo.srt). The narration uses a generated English voice, not a human recording.
