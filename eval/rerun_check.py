from argus.canary import save
from argus.residual import detect
from pathlib import Path
import json

def numeric_outputs(panels: list[dict]) -> list[dict]:
    results = []
    for panel in panels:
        result = {"company": panel["company"]}
        for name, values in panel["metrics"].items():
            residual = detect(values)
            result[name] = {"flags": residual["flags"], "low": residual["low"], "high": residual["high"]}
        results.append(result)
    return results

def evaluate() -> dict:
    panel_path, _ = save(seed=20261018)
    first = json.loads(Path(panel_path).read_text(encoding="utf-8"))
    second = json.loads(Path(panel_path).read_text(encoding="utf-8"))
    a, b = numeric_outputs(first), numeric_outputs(second)
    return {"M14_determinism": 100.0 if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else 0.0,
            "reruns": 2, "source": "seeded synthetic panels read from local cache; real-company determinism remains unmeasured"}
