from argus.residual import detect
from argus.metrics import longest_recent_run

def evaluate() -> dict:
    panels, _ = __import__("argus.canary", fromlist=["generate"]).generate()
    compared = same = 0
    for panel in panels:
        values = panel["metrics"]["receivable_stretch"]
        verdicts = []
        for window in (6, 7, 8):
            subset = values[:window]
            result = detect(subset)
            verdicts.append("flagged" if longest_recent_run(result["flags"]) >= 3 else "clear")
        compared += 1
        same += len(set(verdicts)) == 1
    return {"M13_window_stability": 100 * same / compared, "companies": compared, "status": "measured_synthetic"}
