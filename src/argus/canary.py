"""Seeded synthetic panels for detector evaluation; never presented as real data."""
from __future__ import annotations
import json, random
from pathlib import Path
from .residual import detect
from .metrics import longest_recent_run

TYPES = ("price_led_growth", "receivable_stretch", "inventory_build", "combined")

def generate(seed: int = 20261018, companies: int = 40, periods: int = 8) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    panels, truth = [], []
    for c in range(companies):
        anomaly = c >= companies // 2
        kind = TYPES[(c - companies // 2) % len(TYPES)] if anomaly else None
        start = 5 if anomaly else None
        metrics = {name: [100 + rng.gauss(0, 1.0) for _ in range(periods)] for name in TYPES[:3]}
        if anomaly:
            for i in range(start, periods):
                if kind in ("price_led_growth", "combined"): metrics["price_led_growth"][i] += 16
                if kind in ("receivable_stretch", "combined"): metrics["receivable_stretch"][i] += 20
                if kind in ("inventory_build", "combined"): metrics["inventory_build"][i] += 18
        company_id = f"SYN-{c + 1:03d}"
        panels.append({"company": company_id, "periods": [f"H{i+1}" for i in range(periods)], "metrics": metrics, "synthetic": True})
        truth.append({"company": company_id, "type": kind, "start_period_index": start, "synthetic": True})
    return panels, truth

def save(seed: int = 20261018, out_dir: str | Path = "eval/canary") -> tuple[Path, Path]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    panels, truth = generate(seed)
    panel_path, truth_path = out / "panels.json", out / "ground_truth.json"
    panel_path.write_text(json.dumps(panels, indent=2), encoding="utf-8")
    truth_path.write_text(json.dumps(truth, indent=2), encoding="utf-8")
    return panel_path, truth_path

def run(seed: int = 20261018, out_dir: str | Path = "eval/results") -> dict:
    panels, truth = generate(seed)
    types_correct = starts_correct = detected = false_positive = 0
    errors = []
    for panel, actual in zip(panels, truth):
        per_metric = {}
        for name, values in panel["metrics"].items():
            result = detect(values)
            per_metric[name] = result
        active = [name for name, result in per_metric.items() if longest_recent_run(result["flags"]) >= 3]
        detected_type = active[0] if len(active) == 1 else "combined" if len(active) >= 2 else None
        if actual["type"] is None:
            false_positive += detected_type is not None
            continue
        if detected_type:
            detected += 1
            types_correct += detected_type == actual["type"]
            flagged_indices = [i for i in range(len(panel["periods"])) if any(result["flags"][i] for result in per_metric.values())]
            gap_start = min(flagged_indices) if flagged_indices else len(panel["periods"])
            error = abs(gap_start - actual["start_period_index"])
            errors.append(error)
            starts_correct += detected_type == actual["type"] and error <= 1
    n_positive = sum(x["type"] is not None for x in truth)
    n_clean = len(truth) - n_positive
    result = {"synthetic": True, "seed": seed, "companies": len(panels), "positive_count": n_positive, "clean_count": n_clean,
              "M07_canary_recall": round(100 * starts_correct / n_positive, 2),
              "M07_type_recall": round(100 * types_correct / n_positive, 2),
              "M08_canary_false_positive_rate": round(100 * false_positive / n_clean, 2),
              "M09_gap_start_error": sorted(errors)[len(errors)//2] if errors else None,
              "detected_count": detected, "false_positive_count": false_positive,
              "limitation": "Synthetic anomaly evaluation only; not a measure of real-company finding quality."}
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "canary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
