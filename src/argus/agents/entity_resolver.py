"""LLM-powered entity resolver and company name normalizer for Indian listed companies.

Corrects spelling mistakes, colloquial brand names, and abbreviations into official
BSE/NSE registered corporate entities so intake and forensic screening proceed smoothly.
"""
from __future__ import annotations
import json
import logging
import os
import re
from typing import Optional, Dict, Any
from ..llm import complete, LLMConfigurationError

logger = logging.getLogger("argus.resolver")

KNOWN_CANONICAL_ENTITIES: dict[str, str] = {
    "hul": "Hindustan Unilever Limited",
    "hindustan unilever": "Hindustan Unilever Limited",
    "unilever": "Hindustan Unilever Limited",
    "unilever india": "Hindustan Unilever Limited",
    "itc": "ITC Limited",
    "itc limited": "ITC Limited",
    "nestle": "Nestle India Limited",
    "nestle india": "Nestle India Limited",
    "maggi": "Nestle India Limited",
    "marico": "Marico Limited",
    "marico limited": "Marico Limited",
    "parachute": "Marico Limited",
    "saffola": "Marico Limited",
    "dabur": "Dabur India Limited",
    "dabur india": "Dabur India Limited",
    "bector": "Mrs. Bectors Food Specialities Limited",
    "mrs bector": "Mrs. Bectors Food Specialities Limited",
    "mrs bectors": "Mrs. Bectors Food Specialities Limited",
    "mrs becters": "Mrs. Bectors Food Specialities Limited",
    "bectors food": "Mrs. Bectors Food Specialities Limited",
    "bector food": "Mrs. Bectors Food Specialities Limited",
    "cremica": "Mrs. Bectors Food Specialities Limited",
    "english oven": "Mrs. Bectors Food Specialities Limited",
    "britannia": "Britannia Industries Limited",
    "britannia industries": "Britannia Industries Limited",
    "godrej consumer": "Godrej Consumer Products Limited",
    "godrej consumer products": "Godrej Consumer Products Limited",
    "gcpl": "Godrej Consumer Products Limited",
    "p&g": "Procter & Gamble Hygiene and Health Care Limited",
    "procter": "Procter & Gamble Hygiene and Health Care Limited",
    "procter & gamble": "Procter & Gamble Hygiene and Health Care Limited",
    "procter and gamble": "Procter & Gamble Hygiene and Health Care Limited",
    "pghh": "Procter & Gamble Hygiene and Health Care Limited",
    "united spirits": "United Spirits Limited",
    "usl": "United Spirits Limited",
    "diageo india": "United Spirits Limited",
    "mcdowells": "United Spirits Limited",
    "varun beverages": "Varun Beverages Limited",
    "vbl": "Varun Beverages Limited",
    "tata consumer": "Tata Consumer Products Limited",
    "tata consumer products": "Tata Consumer Products Limited",
    "tataconsum": "Tata Consumer Products Limited",
    "tata tea": "Tata Consumer Products Limited",
    "manpasand": "Manpasand Beverages Limited",
    "manpasand beverages": "Manpasand Beverages Limited",
    "patanjali": "Patanjali Foods Limited",
    "patanjali foods": "Patanjali Foods Limited",
    "ruchi soya": "Patanjali Foods Limited",
    "adani wilmar": "Adani Wilmar Limited",
    "fortune oil": "Adani Wilmar Limited",
    "emami": "Emami Limited",
    "jyothy labs": "Jyothy Labs Limited",
    "colgate": "Colgate-Palmolive (India) Limited",
    "colgate palmolive": "Colgate-Palmolive (India) Limited",
}

def resolve_company_name(query: str, *, offline: bool = False) -> dict[str, Any]:
    """Resolves raw user input (with typos, brands, or abbreviations) into official BSE/NSE name."""
    clean_q = query.strip()
    if not clean_q:
        return {
            "official_name": "",
            "original_query": query,
            "is_corrected": False,
            "ticker": None,
            "confidence": 0.0,
            "source": "empty",
            "explanation": "No company name supplied."
        }

    q_lower = clean_q.lower()

    # 1. Immediate fast-path match in curated dictionary
    if q_lower in KNOWN_CANONICAL_ENTITIES:
        official = KNOWN_CANONICAL_ENTITIES[q_lower]
        is_corr = official.lower() != q_lower
        return {
            "official_name": official,
            "original_query": clean_q,
            "is_corrected": is_corr,
            "ticker": _infer_ticker(official),
            "confidence": 1.0,
            "source": "canonical_alias",
            "explanation": f"Matched canonical FMCG entity '{official}'" if is_corr else "Exact entity match"
        }

    # 2. Check substring / prefix match in known dictionary
    for alias, official in KNOWN_CANONICAL_ENTITIES.items():
        if alias in q_lower or (len(q_lower) >= 4 and q_lower in alias):
            return {
                "official_name": official,
                "original_query": clean_q,
                "is_corrected": official.lower() != q_lower,
                "ticker": _infer_ticker(official),
                "confidence": 0.95,
                "source": "canonical_fuzzy",
                "explanation": f"Matched alias '{clean_q}' to '{official}'"
            }

    # 3. If offline, fallback to title-cased query
    is_offline = offline or os.getenv("ARGUS_OFFLINE", "0") == "1" or not (
        os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("ARGUS_LLM_API_KEY")
    )
    if is_offline:
        formatted = " ".join(w.capitalize() for w in clean_q.split())
        return {
            "official_name": formatted,
            "original_query": clean_q,
            "is_corrected": False,
            "ticker": None,
            "confidence": 0.5,
            "source": "offline_fallback",
            "explanation": "LLM offline; using cleaned raw query."
        }

    # 4. LLM-based entity normalization
    prompt = (
        "You are an Indian stock exchange (BSE/NSE) corporate entity resolution agent.\n"
        "Given the user's search query, correct any spelling mistakes, typos, slang, brand names, or colloquial abbreviations "
        "to identify the exact official, legally registered company name listed on the National Stock Exchange of India (NSE) or Bombay Stock Exchange (BSE), "
        "with an emphasis on Track C (FMCG, Consumer Goods, Food, Beverages, Retail).\n\n"
        f"User input query: \"{clean_q}\"\n\n"
        "Respond ONLY with a valid JSON object in this format (no markdown fences, no conversational text):\n"
        "{\n"
        '  "official_name": "Exact Official Company Name Limited",\n'
        '  "is_corrected": true,\n'
        '  "ticker": "TICKER_SYMBOL",\n'
        '  "confidence": 0.95,\n'
        '  "explanation": "Corrected spelling/abbreviation to official listed entity"\n'
        "}"
    )

    try:
        raw_resp = complete(prompt, model_tier="research")
        # Strip potential markdown formatting
        text = raw_resp.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text.strip())

        official_name = data.get("official_name", "").strip() or clean_q
        is_corrected = bool(data.get("is_corrected", official_name.lower() != q_lower))
        ticker = data.get("ticker") or _infer_ticker(official_name)
        confidence = float(data.get("confidence", 0.9))
        explanation = data.get("explanation") or f"Corrected '{clean_q}' to '{official_name}'"

        return {
            "official_name": official_name,
            "original_query": clean_q,
            "is_corrected": is_corrected,
            "ticker": ticker,
            "confidence": confidence,
            "source": "llm_openrouter",
            "explanation": explanation
        }
    except Exception as exc:
        logger.warning(f"LLM entity resolution error for '{clean_q}': {exc}")
        formatted = " ".join(w.capitalize() for w in clean_q.split())
        return {
            "official_name": formatted,
            "original_query": clean_q,
            "is_corrected": False,
            "ticker": None,
            "confidence": 0.5,
            "source": "error_fallback",
            "explanation": f"LLM error: {exc}"
        }

def _infer_ticker(company_name: str) -> Optional[str]:
    c_low = company_name.lower()
    ticker_map = {
        "hindustan unilever": "HINDUNILVR",
        "itc": "ITC",
        "nestle": "NESTLEIND",
        "marico": "MARICO",
        "dabur": "DABUR",
        "bector": "BECTORFOOD",
        "britannia": "BRITANNIA",
        "godrej consumer": "GODREJCP",
        "procter & gamble": "PGHH",
        "united spirits": "UNITDSPR",
        "varun beverages": "VBL",
        "tata consumer": "TATACONSUM",
        "manpasand": "MANPASAND",
        "patanjali": "PATANJALI",
        "adani wilmar": "AWL",
        "emami": "EMAMILTD",
    }
    for k, v in ticker_map.items():
        if k in c_low:
            return v
    return None
