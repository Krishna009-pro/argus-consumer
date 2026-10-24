from __future__ import annotations
import json
from pathlib import Path
from ..llm import complete, LLMConfigurationError

def plan_queries(candidate: dict) -> list[dict]:
    angles = ", ".join(candidate.get("angles", [])) or "the observed financial gap"
    return [
      {"query": f"{angles} company filings explanation seasonality accounting acquisition", "tag": "supporting"},
      {"query": f"{angles} company gap evidence against benign explanation sector-wide trend", "tag": "disconfirming"},
      {"query": f"{angles} industry prices input costs volume trend alternative explanation", "tag": "disconfirming"},
      {"query": f"{angles} management commentary changes one-off pricing lag", "tag": "supporting"},
    ]

def research(candidate: dict, *, offline: bool = False) -> dict:
    queries = plan_queries(candidate)
    Path("logs").mkdir(exist_ok=True)
    with Path("logs/queries.jsonl").open("a", encoding="utf-8") as f:
        for query in queries: f.write(json.dumps({"candidate_id": candidate.get("id"), **query}) + "\n")
    if offline: return {"queries": queries, "hypotheses": [], "status": "offline_no_llm"}
    prompt = (
        "Given these financial gap angles and available source excerpts, provide competing qualitative explanations only. "
        "Do not include digits, amounts, percentages, dates, computed values, or numerical estimates. "
        "Do not use numbered lists (1., 2.); format strictly as separate dashed bullet points (- ). "
        "Spell out any numbers as words. "
        f"Candidate angles: {angles_text(candidate)}. Available sources: none supplied. Return concise qualitative hypotheses."
    )
    try:
        answer = complete(prompt)
    except (LLMConfigurationError, Exception) as exc:
        return {"queries": queries, "hypotheses": [], "status": "offline_no_llm", "reason": str(exc)}

    import re
    cleaned_lines = []
    for line in answer.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r'^\s*\d+[\.\)]\s*', '', line).lstrip('-*• \t')
        if line:
            cleaned_lines.append(line)

    combined_text = " ".join(cleaned_lines)
    if any(ch.isdigit() for ch in combined_text):
        return {"queries": queries, "hypotheses": [], "status": "rejected_numeric_llm_output"}
    return {"queries": queries, "hypotheses": cleaned_lines if cleaned_lines else [answer], "status": "completed_no_retrieved_sources"}

def angles_text(candidate: dict) -> str: return ", ".join(candidate.get("angles", []))
