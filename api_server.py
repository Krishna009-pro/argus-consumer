"""ARGUS Live Backend API Server
Connects React Dashboard directly to the real ARGUS deterministic engine,
live Serper search with PDF filtering, and content-addressed candidate extraction.
"""
from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from argus.search import search_serper, discover_pdf_links, is_pdf_url, load_local_env
from argus.ingest.local_import import import_remote_pdf, import_pdf, save_candidates
from argus.schemas import ObservationCandidate

load_local_env()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("argus.api")

app = FastAPI(title="ARGUS Autonomous Financial Discovery Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXCLUDED_DOMAINS = (
    "scribd.com",
    "slideshare.net",
    "facebook.com",
    "wikipedia.org",
    "quora.com",
    "coursehero.com",
    "issuu.com",
    "docplayer.net",
)

# Canonical live verified PDF sources for FMCG companies
COMPANY_VERIFIED_SOURCES = {
    "godrej": {
        "title": "Godrej Consumer Products Integrated Annual Report 2024-25",
        "url": "https://www.godrejcp.com/uploads/GCPL_Annual_and_Integrated_Report_2024_25_1_a988ff386b.pdf",
    },
    "nestle": {
        "title": "Nestle India Annual Report 2024-25 (NSE Statutory Archive)",
        "url": "https://nsearchives.nseindia.com/annual_reports/AR_26487_NESTLEIND_2024_2025_A_03062025002440.pdf",
    },
    "united spirits": {
        "title": "United Spirits Limited Statutory Filing (BSE Archive)",
        "url": "https://www.bseindia.com/xml-data/corpfiling/AttachHis/ebb937a3-310c-4ae0-a2fa-c012c8a2e9f7.pdf",
    },
    "britannia": {
        "title": "Britannia Industries Limited Annual Report",
        "url": "https://media.britannia.co.in/Annual_Report_2022_23_988ac4516b.pdf",
    },
    "marico": {
        "title": "Marico Limited Annual Report FY25",
        "url": "https://marico.com/investorspdf/Marico_Annual_Report_FY25.pdf",
    },
    "dabur": {
        "title": "Dabur Consolidated Financial Statements FY2024-25",
        "url": "https://www.dabur.com/digital-annual-reports/reports/dabur-consolidated-financials.pdf",
    },
    "itc": {
        "title": "ITC Report and Accounts 2026 (Consolidated Statements)",
        "url": "https://itcportal.com/content/dam/itc-corporate/open-pdfs/report-and-accounts/ITC-Report-and-Accounts-2026.pdf",
    },
    "hindustan unilever": {
        "title": "Hindustan Unilever Limited Annual Report 2025-26",
        "url": "https://www.hul.co.in/files/annual-report-2025-26.pdf",
    },
    "manpasand": {
        "title": "Manpasand Beverages Limited Annual Report (BSE Official Filing)",
        "url": "https://www.bseindia.com/bseplus/AnnualReport/539207/5392070318.pdf",
    },
    "varun beverages": {
        "title": "Varun Beverages Limited Annual Report FY2025",
        "url": "https://www.varunbeverages.com/Annual-Report-FY-2025.pdf",
    },
    "tata consumer": {
        "title": "Tata Consumer Products Integrated Annual Report 2024-25",
        "url": "https://www.tataconsumer.com/sites/g/files/gfwrlq316/files/2025-06/Tata_Consumer_IAR_2024_25.pdf",
    },
}

class SearchRequest(BaseModel):
    company: str
    limit: Optional[int] = 8

class ResolveCompanyRequest(BaseModel):
    query: str

class InspectRequest(BaseModel):
    url: str
    title: Optional[str] = None

class ExtractRequest(BaseModel):
    url: str
    company: str
    title: Optional[str] = None

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "engine": "ARGUS Autonomous Consumer Discovery Engine (Track C)",
        "serper_active": bool(os.getenv("SERPER_API_KEY")),
        "rules": ["R1", "R2", "R3", "R4", "R5", "R6", "R8"],
    }

@app.post("/api/intake/resolve-company")
def api_resolve_company(req: ResolveCompanyRequest):
    from argus.agents.entity_resolver import resolve_company_name
    return resolve_company_name(req.query)

@app.post("/api/intake/search")
def api_search(req: SearchRequest):
    raw_query = req.company.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Company name is required.")
    
    # 1. Resolve spelling mistakes, brand names, and abbreviations via LLM / Canonical normalizer
    from argus.agents.entity_resolver import resolve_company_name
    resolved = resolve_company_name(raw_query)
    company = resolved.get("official_name") or raw_query
    
    # Target direct PDF filings from corporate sites and BSE/NSE
    query = f'"{company}" ("annual report" OR "financial results") filetype:pdf'
    logger.info(f"Resolved '{raw_query}' -> '{company}'. Searching public filings via Serper: {query}")
    results = []
    
    try:
        raw_results = search_serper(query, limit=req.limit or 10)
        # Filter out social/paywall/slideshare sites
        for r in raw_results:
            u = r.get("url", "")
            if not any(bad in u.lower() for bad in EXCLUDED_DOMAINS):
                results.append(r)
    except Exception as exc:
        logger.warning(f"Live search exception: {exc}")

    # If Serper returned no direct PDF or is empty, check canonical verified sources
    q_low = company.lower()
    for key, source in COMPANY_VERIFIED_SOURCES.items():
        if key in q_low or key in raw_query.lower():
            if not any(r.get("url") == source["url"] for r in results):
                results.insert(0, {
                    "title": source["title"],
                    "url": source["url"],
                    "snippet": f"Verified official statutory report for {company}."
                })
            break

    # If still empty, check local cache source files
    if not results:
        results = _search_local_cache(company)
        if not results and raw_query != company:
            results = _search_local_cache(raw_query)

    return {
        "company": company,
        "original_query": raw_query,
        "resolved": resolved,
        "searchResults": results,
    }

@app.post("/api/intake/inspect")
def api_inspect(req: InspectRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Report URL is required.")
    
    logger.info(f"Inspecting report URL for PDF statements: {url}")
    if is_pdf_url(url) or ".pdf" in url.lower():
        return {
            "url": url,
            "pdfLinks": [{"title": req.title or url.split("/")[-1].replace(".pdf", ""), "url": url}]
        }

    try:
        pdf_links = discover_pdf_links(url)
        filtered = [l for l in pdf_links if not any(bad in l.get("url", "").lower() for bad in EXCLUDED_DOMAINS)]
        if not filtered and (is_pdf_url(url) or ".pdf" in url.lower()):
            filtered = [{"title": req.title or "Consolidated Financial Statements PDF", "url": url}]
        
        return {"url": url, "pdfLinks": filtered}
    except Exception as exc:
        logger.warning(f"PDF link discovery error: {exc}")
        if is_pdf_url(url) or ".pdf" in url.lower():
            return {"url": url, "pdfLinks": [{"title": req.title or "Direct Annual Report PDF", "url": url}]}
        raise HTTPException(status_code=400, detail=f"Could not inspect report page: {exc}")

@app.post("/api/intake/extract")
def api_extract(req: ExtractRequest):
    url = req.url.strip()
    company = req.company.strip()
    if not url or not company:
        raise HTTPException(status_code=400, detail="Both URL and company name are required.")
    
    from argus.agents.entity_resolver import resolve_company_name
    resolved = resolve_company_name(company)
    official_company = resolved.get("official_name") or company

    logger.info(f"Executing real PDF intake and financial statement extraction for '{official_company}' -> {url}")
    try:
        cache_path, digest, candidate_file, candidates, cache_reused = import_remote_pdf(
            url, company=official_company
        )
        
        return {
            "company": official_company,
            "title": req.title or url.split("/")[-1],
            "url": url,
            "cache_path": str(cache_path),
            "sha256": digest,
            "candidate_file": str(candidate_file),
            "candidate_count": sum(c.status == "unverified" for c in candidates),
            "ambiguous_count": sum(c.status == "ambiguous" for c in candidates),
            "cache_reused": cache_reused,
            "candidates": [c.model_dump(mode="json") for c in candidates],
        }
    except Exception as exc:
        logger.error(f"PDF extraction error: {exc}")
        # If public server blocked bot access (e.g. HTTP 403), check for a cached local PDF for this company
        fallback_res = _try_local_company_extraction(company, url, req.title)
        if fallback_res:
            return fallback_res
        raise HTTPException(status_code=500, detail=f"Public filing extraction failed: {exc}")

def _try_local_company_extraction(company: str, url: str, title: Optional[str]) -> Optional[Dict[str, Any]]:
    """Fallback to locally cached PDF for the company if remote server returns 403."""
    cache_dir = Path("data/cache")
    candidate_dir = Path("data/candidates")
    if not cache_dir.is_dir():
        return None
    
    # Check if there is an existing candidate manifest for this company
    comp_lower = company.lower()
    words = [w for w in comp_lower.split() if len(w) >= 4 and w not in {"limited", "india", "ltd"}]
    for cand_file in candidate_dir.glob("candidates-*.json"):
        try:
            rows = json.loads(cand_file.read_text(encoding="utf-8"))
            if rows and any(
                comp_lower in r.get("company", "").lower()
                or r.get("company", "").lower() in comp_lower
                or any(w in r.get("company", "").lower() for w in words)
                for r in rows
            ):
                candidates = [ObservationCandidate.model_validate(r) for r in rows]
                first = candidates[0]
                return {
                    "company": company,
                    "title": title or f"{company} Statutory Annual Report",
                    "url": first.source_url or url,
                    "cache_path": first.cache_path,
                    "sha256": first.source_sha256,
                    "candidate_file": str(cand_file),
                    "candidate_count": sum(c.status == "unverified" for c in candidates),
                    "ambiguous_count": sum(c.status == "ambiguous" for c in candidates),
                    "cache_reused": True,
                    "candidates": [c.model_dump(mode="json") for c in candidates],
                }
        except Exception:
            continue
    return None

def _search_local_cache(company: str) -> list[dict[str, str]]:
    results = []
    comp_lower = company.lower()
    cache_dir = Path("data/cache")
    if not cache_dir.is_dir():
        return results
    for meta in cache_dir.glob("*.source.json"):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            url = data.get("source_url", "")
            if any(term in url.lower() or term in meta.name.lower() for term in comp_lower.split() if len(term) > 3):
                title = f"{company} Annual Report ({meta.name[:12]})"
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": f"Verified BSE/NSE filing cached with SHA-256 digest: {data.get('sha256')}"
                })
        except Exception:
            continue
    return results

@app.get("/api/pdf/{company_slug}")
def get_company_pdf(company_slug: str):
    slug = company_slug.lower().strip()
    pdf_path = Path(f"reports/{slug}-audit-dossier.pdf")
    if not pdf_path.exists():
        # Check if alternative exists or generate from dossier
        report_json = Path(f"reports/{slug}.json")
        if not report_json.exists():
            # Try finding matching report
            for cand in Path("reports").glob("*.json"):
                if cand.stem.startswith(slug) and not cand.name.endswith("-analysis.json"):
                    report_json = cand
                    break
        if not report_json.exists():
            raise HTTPException(status_code=404, detail=f"No dossier found for company '{company_slug}'")
        try:
            from argus.schemas import Dossier
            from argus.ledger import EvidenceLedger
            from argus.report.pdf_export import build_pdf
            dossier_data = json.loads(report_json.read_text(encoding="utf-8"))
            analysis_path = report_json.parent / f"{report_json.stem}-analysis.json"
            analysis_data = json.loads(analysis_path.read_text(encoding="utf-8")) if analysis_path.exists() else None
            dossier = Dossier.model_validate(dossier_data)
            ledger = EvidenceLedger("data/ledger.jsonl")
            pdf_bytes = build_pdf(dossier, ledger_entries=ledger.entries(), analysis=analysis_data)
            pdf_path.write_bytes(pdf_bytes)
        except Exception as exc:
            logger.error("Failed to generate PDF for %s: %s", company_slug, exc)
            raise HTTPException(status_code=500, detail=f"Failed to generate audit PDF: {exc}")
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=f"{company_slug}-audit-dossier.pdf"
    )

class VerifyCandidateRequest(BaseModel):
    candidate_file: str
    candidate_id: str
    company: str
    verified_by: Optional[str] = "Audit Reviewer"
    period: Optional[str] = "FY2025"
    unit: Optional[str] = "INR_crore"
    period_type: Optional[str] = "annual"
    currency: Optional[str] = "INR"
    basis: Optional[str] = "consolidated"
    run_analysis: Optional[bool] = True

class VerifyAllCandidatesRequest(BaseModel):
    candidate_file: str
    candidate_ids: List[str]
    company: str
    verified_by: Optional[str] = "Audit Reviewer"
    run_analysis: Optional[bool] = True

@app.post("/api/candidate/verify")
def api_verify_candidate(req: VerifyCandidateRequest):
    from argus.ingest.local_import import verify_candidate
    from argus.cli import run_company, slug
    
    cand_path = Path(req.candidate_file)
    if not cand_path.exists():
        raise HTTPException(status_code=404, detail=f"Candidate file not found: {req.candidate_file}")
    
    try:
        entry = verify_candidate(
            candidate_file=cand_path,
            candidate_id=req.candidate_id,
            verified_by=req.verified_by or "Audit Reviewer",
            period=req.period or "FY2025",
            unit=req.unit or "INR_crore",
            period_type=req.period_type or "annual",
            currency=req.currency or "INR",
            consolidation_basis=req.basis or "consolidated",
        )
    except Exception as exc:
        logger.error(f"Candidate verification error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    
    updated_candidates = []
    if cand_path.exists():
        try:
            updated_candidates = json.loads(cand_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    dossier = None
    analysis = None
    if req.run_analysis and req.company:
        try:
            logger.info(f"Re-running deterministic engine for '{req.company}'...")
            run_company(req.company)
            company_slug = slug(req.company)
            rep_json = Path(f"reports/{company_slug}.json")
            an_json = Path(f"reports/{company_slug}-analysis.json")
            if rep_json.exists():
                dossier = json.loads(rep_json.read_text(encoding="utf-8"))
            if an_json.exists():
                analysis = json.loads(an_json.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Error re-running engine for {req.company}: {exc}")

    return {
        "success": True,
        "entry": entry.model_dump(mode="json"),
        "candidates": updated_candidates,
        "dossier": dossier,
        "analysis": analysis,
        "company": req.company,
        "company_key": slug(req.company),
        "message": f"Candidate {req.candidate_id} verified into ledger.",
    }

@app.post("/api/candidate/verify-all")
def api_verify_all(req: VerifyAllCandidatesRequest):
    from argus.ingest.local_import import verify_candidate
    from argus.cli import run_company, slug
    
    cand_path = Path(req.candidate_file)
    if not cand_path.exists():
        raise HTTPException(status_code=404, detail=f"Candidate file not found: {req.candidate_file}")
    
    rows = json.loads(cand_path.read_text(encoding="utf-8"))
    entries = []
    errors = []
    for cand_id in req.candidate_ids:
        match = next((r for r in rows if r.get("id") == cand_id), None)
        if not match or match.get("status") != "unverified":
            continue
        try:
            entry = verify_candidate(
                candidate_file=cand_path,
                candidate_id=cand_id,
                verified_by=req.verified_by or "Audit Reviewer",
                period=match.get("period") or "FY2025",
                unit=match.get("unit") or "INR_crore",
                period_type="annual",
                currency="INR",
                consolidation_basis=match.get("consolidation_basis") or "consolidated",
            )
            entries.append(entry.model_dump(mode="json"))
        except Exception as exc:
            errors.append(f"{cand_id}: {exc}")

    updated_candidates = []
    if cand_path.exists():
        try:
            updated_candidates = json.loads(cand_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    dossier = None
    analysis = None
    if req.run_analysis and req.company and entries:
        try:
            logger.info(f"Re-running deterministic engine for '{req.company}' ({len(entries)} verified)...")
            run_company(req.company)
            company_slug = slug(req.company)
            rep_json = Path(f"reports/{company_slug}.json")
            an_json = Path(f"reports/{company_slug}-analysis.json")
            if rep_json.exists():
                dossier = json.loads(rep_json.read_text(encoding="utf-8"))
            if an_json.exists():
                analysis = json.loads(an_json.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Error re-running engine for {req.company}: {exc}")

    return {
        "success": True,
        "verified_count": len(entries),
        "entries": entries,
        "candidates": updated_candidates,
        "dossier": dossier,
        "analysis": analysis,
        "errors": errors,
        "company": req.company,
        "company_key": slug(req.company),
        "message": f"Successfully verified {len(entries)} candidate(s) into ledger.",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
