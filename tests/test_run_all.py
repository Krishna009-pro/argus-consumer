from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from eval.run_all import measure


class RunAllEvaluationTests(unittest.TestCase):
    def test_measures_distinct_verified_company_runs_and_median_latency(self):
        entries = [SimpleNamespace(company="Company A"), SimpleNamespace(company="company a"),
                   SimpleNamespace(company="Company B"), SimpleNamespace(company=None)]
        with tempfile.TemporaryDirectory() as directory:
            def run(company, _entries):
                base = Path(directory) / company
                base.with_suffix(".md").write_text("dossier", encoding="utf-8")
                base.with_suffix(".json").write_text("{}", encoding="utf-8")
                base.with_name(f"{base.name}-analysis.json").write_text("{}", encoding="utf-8")
                return {"company": company, "dossier": str(base.with_suffix(".md")),
                        "verified_entries": 2, "elapsed_seconds": 10 if company == "Company A" else 20}

            result = measure(entries, run)

        self.assertEqual(result["M05_companies_end_to_end"], 2)
        self.assertEqual(result["company_count"], 2)
        self.assertEqual(result["M15_live_latency_seconds"], 15)
        self.assertEqual(result["status"], "measured")

    def test_failed_company_is_reported_without_counting_as_complete(self):
        entries = [SimpleNamespace(company="Company A"), SimpleNamespace(company="Company B")]

        def run(company, _entries):
            if company == "Company A":
                raise RuntimeError("fixture failure")
            return {"company": company, "dossier": "missing.md", "verified_entries": 0,
                    "elapsed_seconds": 1}

        result = measure(entries, run)
        self.assertEqual(result["M05_companies_end_to_end"], 0)
        self.assertEqual([row["complete"] for row in result["companies"]], [False, False])
        self.assertIn("fixture failure", result["companies"][0]["error"])


if __name__ == "__main__":
    unittest.main()
