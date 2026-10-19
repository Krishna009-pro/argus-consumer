"""Import local public filings into a content-addressed cache as unverified candidates."""
from __future__ import annotations
import csv, hashlib, json, shutil
from pathlib import Path
from typing import Iterable
from datetime import datetime, timezone
from ..ledger import EvidenceLedger
from ..schemas import LedgerEntry
from ..schemas import ObservationCandidate

CSV_FIELDS = {"metric", "value", "unit", "period", "snippet"}

def cache_local_file(source: str | Path, cache_dir: str | Path = "data/cache") -> tuple[Path, str]:
    source = Path(source)
    if not source.is_file(): raise FileNotFoundError(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = Path(cache_dir) / f"{digest}{source.suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): shutil.copyfile(source, target)
    return target, digest

def _cache_source_metadata(cache_path: Path, url: str, digest: str) -> None:
    metadata_path = Path(f"{cache_path}.source.json")
    metadata_path.write_text(json.dumps({"source_url": url, "sha256": digest,
        "cache_path": str(cache_path)}, indent=2), encoding="utf-8")

def _find_source_cache(url: str, cache_dir: str | Path) -> tuple[Path, str] | None:
    root = Path(cache_dir)
    if not root.is_dir(): return None
    for metadata_path in root.glob("*.pdf.source.json"):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            path = Path(metadata["cache_path"])
            digest = metadata["sha256"]
            if metadata.get("source_url") != url or not path.is_file(): continue
            if EvidenceLedger.sha256(path) != digest or b"%PDF-" not in path.read_bytes()[:1024]: continue
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                if not pdf.pages: continue
            return path, digest
        except (OSError, ValueError, KeyError, ImportError):
            continue
        except Exception:
            # A corrupt or truncated source is not a reusable cache hit.
            continue
    return None

def _candidate(index: int, *, company: str, source_url: str, source_type: str, cache_path: Path,
               digest: str, **fields) -> ObservationCandidate:
    identity = fields.pop("_identity", "")
    claim_material = json.dumps([company.casefold(), source_url, source_type, fields, identity],
                                sort_keys=True, separators=(",", ":"), default=str)
    claim_hash = hashlib.sha256(claim_material.encode("utf-8")).hexdigest()[:12]
    return ObservationCandidate(id=f"C-{digest[:12]}-{claim_hash}", company=company,
      source_url=source_url, source_type=source_type, cache_path=str(cache_path), source_sha256=digest,
      status="unverified", **fields)

def import_csv(path: str | Path, *, company: str, source_url: str, source_type: str = "filing",
               cache_dir: str | Path = "data/cache") -> tuple[Path, list[ObservationCandidate]]:
    source = Path(path)
    cache_path, digest = cache_local_file(source, cache_dir)
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    if not lines: raise ValueError("Observation CSV is empty.")
    headers = next(csv.reader([lines[0]]))
    missing = CSV_FIELDS - {h.strip().lower() for h in headers}
    if missing: raise ValueError(f"Observation CSV is missing required columns: {', '.join(sorted(missing))}")
    candidates = []
    for idx, row in enumerate(csv.DictReader(lines), start=2):
        clean = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        snippet = clean.get("snippet", "")
        if not snippet or snippet not in "\n".join(lines):
            raise ValueError(f"CSV row {idx} lacks a literal source snippet.")
        try: value = float(clean["value"].replace(",", "")) if clean.get("value") else None
        except ValueError: value = None
        status = "unverified" if value is not None else "missing"
        candidates.append(_candidate(idx, company=company, source_url=source_url, source_type=source_type,
          cache_path=cache_path, digest=digest, metric=clean.get("metric") or "unknown", value=value,
          unit=clean.get("unit") or None, period=clean.get("period") or None, period_type=clean.get("period_type") or None,
          period_start=clean.get("period_start") or None, period_end=clean.get("period_end") or None,
          currency=clean.get("currency") or None, consolidation_basis=clean.get("consolidation_basis") or "unknown",
          doc_page=int(clean["page"]) if clean.get("page", "").isdigit() else None, snippet=snippet,
          notes=["Imported from local structured data; verify value, context, units, period and basis against the official source."]))
    return cache_path, candidates

def import_pdf(path: str | Path, *, company: str, source_url: str, source_type: str = "filing",
               cache_dir: str | Path = "data/cache") -> tuple[Path, list[ObservationCandidate]]:
    from .pdf_tables import extract
    cache_path, digest = cache_local_file(path, cache_dir)
    proposals = extract(cache_path)
    candidates = []
    for idx, item in enumerate(proposals, start=1):
        candidates.append(_candidate(idx, company=company, source_url=source_url, source_type=source_type,
          cache_path=cache_path, digest=digest, metric=item["metric"], value=item.get("value"), unit=None,
          period=None, period_type=None, doc_page=item["page"], snippet=item["snippet"],
          _identity=f"{item.get('period_header', '')}|{item.get('column_header', '')}",
          notes=[item["warning"],
                 *([f"Dated column header year: {item['period_header']}."] if item.get("period_header") else []),
                 *([f"Statement header: {item['column_header']}"] if item.get("column_header") else []),
                 "No value is verified until a human resolves the period, units, statement basis and table alignment."]))
    return cache_path, candidates

def import_local(path: str | Path, *, company: str, source_url: str, source_type: str = "filing",
                 cache_dir: str | Path = "data/cache") -> tuple[Path, list[ObservationCandidate]]:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv": return import_csv(path, company=company, source_url=source_url, source_type=source_type, cache_dir=cache_dir)
    if suffix == ".pdf": return import_pdf(path, company=company, source_url=source_url, source_type=source_type, cache_dir=cache_dir)
    raise ValueError("Supported local inputs are CSV observation extracts and PDF filings.")

def import_remote_pdf(url: str, *, company: str, source_type: str = "filing",
                      cache_dir: str | Path = "data/cache",
                      candidate_dir: str | Path = "data/candidates") -> tuple[Path, str, Path, list[ObservationCandidate], bool]:
    """Reuse an exact cached source or fetch a public PDF and emit unverified candidates."""
    from ..search import discover_pdf_links, is_pdf_url
    if not is_pdf_url(url):
        linked_pdfs = discover_pdf_links(url)
        if len(linked_pdfs) == 1:
            url = linked_pdfs[0]["url"]
        elif linked_pdfs:
            urls = "\n".join(f"- {item['title']}: {item['url']}" for item in linked_pdfs)
            raise ValueError(f"The selected page links to multiple PDFs; choose one direct PDF URL:\n{urls}")
        else:
            raise ValueError("Selected source is a web page and no direct PDF report link was found; no file was cached.")
    candidate_root = Path(candidate_dir)
    cached_source = _find_source_cache(url, cache_dir)
    if cached_source:
        cache_path, digest = cached_source
        # Reuse the matching review manifest before paying the cost of reparsing
        # a long annual report on a dashboard rerun.
        if candidate_root.is_dir():
            for manifest in candidate_root.glob("candidates-*.json"):
                try:
                    prior_rows = json.loads(manifest.read_text(encoding="utf-8"))
                    matching = [row for row in prior_rows if row.get("source_url") == url
                                and (row.get("company") or "").casefold() == company.casefold()
                                and row.get("source_sha256") == digest
                                and Path(row.get("cache_path", "")) == cache_path]
                    if matching and len(matching) == len(prior_rows):
                        persisted = [ObservationCandidate.model_validate(row) for row in prior_rows]
                        return cache_path, digest, manifest, persisted, True
                except (OSError, ValueError, TypeError):
                    continue
        imported_path, candidates = import_pdf(cache_path, company=company, source_url=url,
            source_type=source_type, cache_dir=cache_dir)
        candidate_path = save_candidates(candidates, candidate_root)
        persisted = [ObservationCandidate.model_validate(row) for row in
            json.loads(candidate_path.read_text(encoding="utf-8"))]
        return imported_path, digest, candidate_path, persisted, True
    if candidate_root.is_dir():
        for manifest in candidate_root.glob("candidates-*.json"):
            try:
                prior_rows = json.loads(manifest.read_text(encoding="utf-8"))
                matching = [row for row in prior_rows if row.get("source_url") == url
                            and (row.get("company") or "").casefold() == company.casefold()]
                if not matching:
                    continue
                digest = matching[0].get("source_sha256")
                cached = Path(matching[0].get("cache_path", ""))
                if not digest or any(row.get("source_sha256") != digest for row in matching):
                    continue
                if cached.is_file() and EvidenceLedger.sha256(cached) == digest:
                    if len(matching) == len(prior_rows):
                        persisted = [ObservationCandidate.model_validate(row) for row in prior_rows]
                        return cached, digest, manifest, persisted, True
                    _, fresh = import_pdf(cached, company=company, source_url=url,
                        source_type=source_type, cache_dir=cache_dir)
                    candidate_path = save_candidates(fresh, candidate_root)
                    persisted = [ObservationCandidate.model_validate(row) for row in
                        json.loads(candidate_path.read_text(encoding="utf-8"))]
                    return cached, digest, candidate_path, persisted, True
            except (OSError, ValueError, TypeError):
                continue
    from .cache import fetch
    cache_path, digest = fetch(url, cache_dir=cache_dir)
    if cache_path.suffix.lower() != ".pdf" or b"%PDF-" not in cache_path.read_bytes()[:1024]:
        raise ValueError("Selected public source is not a PDF report; it remains cached but no candidates were created.")
    _cache_source_metadata(cache_path, url, digest)
    imported_path, candidates = import_pdf(cache_path, company=company, source_url=url,
        source_type=source_type, cache_dir=cache_dir)
    candidate_path = save_candidates(candidates, candidate_dir)
    persisted = [ObservationCandidate.model_validate(row) for row in
        json.loads(candidate_path.read_text(encoding="utf-8"))]
    return imported_path, digest, candidate_path, persisted, False

def save_candidates(candidates: Iterable[ObservationCandidate], output_dir: str | Path = "data/candidates") -> Path:
    rows = list(candidates)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    digest_prefix = rows[0].source_sha256[:12] if rows else "empty"
    company = rows[0].company if rows else ""
    company_key = hashlib.sha256(company.casefold().encode("utf-8")).hexdigest()[:8] if company else "none"
    target = out / f"candidates-{digest_prefix}-{company_key}.json"
    legacy = out / f"candidates-{digest_prefix}.json"
    if not target.exists() and legacy.is_file():
        try:
            legacy_rows = json.loads(legacy.read_text(encoding="utf-8"))
            if any(row.get("company", "").casefold() == company.casefold()
                   and row.get("source_url") == (rows[0].source_url if rows else None)
                   for row in legacy_rows):
                target = legacy
        except (OSError, ValueError, TypeError):
            pass
    current = [r.model_dump(mode="json") for r in rows]
    if target.exists():
        prior_rows = json.loads(target.read_text(encoding="utf-8"))
        prior_by_id = {row.get("id"): row for row in prior_rows}
        current_ids = {row["id"] for row in current}
        stable_fields = ("metric", "value", "doc_page", "snippet", "source_url", "source_sha256", "company")
        for row in current:
            prior = prior_by_id.get(row["id"])
            if prior is None:
                continue
            if all(prior.get(field) == row.get(field) for field in stable_fields):
                row["status"] = prior.get("status", row["status"])
                row["notes"] = list(dict.fromkeys([*row.get("notes", []), *prior.get("notes", [])]))
            else:
                row["notes"].append("Prior review was not carried forward because the extracted claim changed; review this version again.")
        for prior in prior_rows:
            if prior.get("id") in current_ids:
                continue
            if prior.get("status") in {"unverified", "missing"}:
                prior["status"] = "ambiguous"
                prior.setdefault("notes", []).append("This claim was not emitted by the current extraction pass; retained for audit and not eligible for approval.")
            current.append(prior)
    target.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return target

def verify_candidate(candidate_file: str | Path, candidate_id: str, *, verified_by: str,
                     period: str, unit: str, period_type: str, currency: str,
                     consolidation_basis: str, period_start: str | None = None,
                     period_end: str | None = None, denominator: str | None = None,
                     reporting_scope: str | None = None, comparability_cohort: str | None = None,
                     comparability_note: str | None = None,
                     ledger_path: str | Path = "data/ledger.jsonl") -> LedgerEntry:
    rows = json.loads(Path(candidate_file).read_text(encoding="utf-8"))
    match = next((r for r in rows if r.get("id") == candidate_id), None)
    if match is None: raise KeyError(f"Candidate not found: {candidate_id}")
    candidate = ObservationCandidate.model_validate(match)
    if candidate.status != "unverified" or candidate.value is None:
        raise ValueError("Only unverified candidates with an extracted value may be reviewed into the ledger.")
    cached = Path(candidate.cache_path)
    ledger = EvidenceLedger(ledger_path)
    if not cached.is_file() or ledger.sha256(cached) != candidate.source_sha256:
        raise ValueError("Cached source is absent or its SHA-256 no longer matches the candidate.")
    if candidate.doc_page is None: raise ValueError("A verified filing observation requires a real source page.")
    provisional = LedgerEntry(id="review", metric=candidate.metric, value=candidate.value, unit=unit, period=period,
      source_url=candidate.source_url, source_type=candidate.source_type, doc_page=candidate.doc_page,
      snippet=candidate.snippet, source_sha256=candidate.source_sha256, cache_path=str(cached), company=candidate.company,
      period_type=period_type, period_start=period_start, period_end=period_end, currency=currency,
      consolidation_basis=consolidation_basis, verified=True, verified_by=verified_by,
      verified_at=datetime.now(timezone.utc), denominator=denominator, reporting_scope=reporting_scope,
      comparability_cohort=comparability_cohort, comparability_note=comparability_note)
    from .source_text import snippet_is_cached
    if not snippet_is_cached(provisional.cache_path, provisional.snippet, provisional.doc_page):
        raise ValueError("The candidate snippet is not present verbatim in the cached source.")
    entry = provisional.model_copy(update={"id": ledger.next_id()})
    ledger.append(entry)
    for row in rows:
        if row.get("id") == candidate_id:
            row["status"] = "verified"; row["notes"] = [*row.get("notes", []), f"Manually reviewed by {verified_by} at {entry.verified_at.isoformat()}."]
            break
    Path(candidate_file).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return entry

def link_candidate(candidate_file: str | Path, candidate_id: str, ledger_entry_id: str, *,
                   ledger_path: str | Path = "data/ledger.jsonl") -> ObservationCandidate:
    """Link an extracted proposal to an already-reviewed ledger row without duplicating it."""
    path = Path(candidate_file)
    rows = json.loads(path.read_text(encoding="utf-8"))
    match = next((row for row in rows if row.get("id") == candidate_id), None)
    if match is None:
        raise KeyError(f"Candidate not found: {candidate_id}")
    candidate = ObservationCandidate.model_validate(match)
    if candidate.status != "unverified" or candidate.value is None:
        raise ValueError("Only unverified candidates with an extracted value may be linked.")

    ledger = EvidenceLedger(ledger_path)
    entry = ledger.get(ledger_entry_id)
    if entry is None or not entry.verified or not entry.verified_by or not entry.verified_at:
        raise ValueError("The target ledger row is absent or not manually verified.")
    if not ledger.verify(entry):
        raise ValueError("The target ledger row's cached-source hash no longer matches.")

    exact_fields = {
        "company": (candidate.company.casefold(), (entry.company or "").casefold()),
        "metric": (candidate.metric, entry.metric),
        "value": (candidate.value, entry.value),
        "source_url": (candidate.source_url, entry.source_url),
        "source_type": (candidate.source_type, entry.source_type),
        "doc_page": (candidate.doc_page, entry.doc_page),
        "source_sha256": (candidate.source_sha256, entry.source_sha256),
    }
    mismatched = [name for name, (left, right) in exact_fields.items() if left != right]
    if mismatched:
        raise ValueError("Candidate does not exactly match the verified ledger evidence fields: " + ", ".join(mismatched))

    from .source_text import snippet_contains_value, snippet_is_cached
    if not (snippet_is_cached(candidate.cache_path, candidate.snippet, candidate.doc_page)
            and snippet_contains_value(candidate.snippet, candidate.value)
            and snippet_is_cached(entry.cache_path, entry.snippet, entry.doc_page)
            and snippet_contains_value(entry.snippet, entry.value)):
        raise ValueError("Candidate or ledger evidence snippet is not source-backed on the cited page.")

    cached = Path(candidate.cache_path)
    if not cached.is_file() or EvidenceLedger.sha256(cached) != candidate.source_sha256:
        raise ValueError("Candidate cached source is absent or its SHA-256 no longer matches.")

    linked = candidate.model_copy(update={
        "unit": entry.unit,
        "period": entry.period,
        "period_type": entry.period_type,
        "period_start": entry.period_start,
        "period_end": entry.period_end,
        "currency": entry.currency,
        "consolidation_basis": entry.consolidation_basis,
        "status": "verified",
        "ledger_entry_id": entry.id,
        "notes": [*candidate.notes, f"Linked to manually verified ledger entry {entry.id}; no duplicate observation was written."],
    })
    for index, row in enumerate(rows):
        if row.get("id") == candidate_id:
            rows[index] = linked.model_dump(mode="json")
            break
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return linked
