import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from argus.metrics import receivable_days
from eval.reconcile import _engine_value, evaluate


class ReconciliationTests(unittest.TestCase):
    def test_gcpl_turnover_ratios_are_excluded_when_formulas_differ(self):
        dataset = json.loads(Path("data/reconciliation/published_figures.json").read_text(encoding="utf-8"))
        refs = dataset["references"]
        self.assertEqual(len(refs), 4)
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "source.pdf"
            cache.write_bytes(b"fixture")
            for ref in refs:
                ref.update({"cache_path": str(cache), "source_sha256": "fixture-hash", "page": 1,
                            "formula_page": 2, "snippet": "verified published value",
                            "formula_snippet": "average opening and closing balance"})
            path = Path(tmp) / "references.json"
            path.write_text(json.dumps(dataset), encoding="utf-8")

            class FakePage:
                def __init__(self, text): self.text = text
                def extract_text(self): return self.text

            class FakeReader:
                pages = [FakePage("verified published value"), FakePage("average opening and closing balance")]

            with patch("eval.reconcile.EvidenceLedger.sha256", return_value="fixture-hash"), \
                 patch("eval.reconcile._open_reader", return_value=FakeReader()):
                result = evaluate(path)
        self.assertIsNone(result["value"])
        self.assertEqual((result["matched"], result["compared"], result["excluded"]), (0, 0, 4))
        self.assertEqual(result["status"], "unavailable_no_comparable_published_figures")
        self.assertTrue(all(row["reason"] == "published and ARGUS formulas differ" for row in result["exclusions"]))

    def test_supported_reconciliation_formula_recomputes_from_exact_inputs(self):
        rows = [
            SimpleNamespace(company="Example", period="FY2025", consolidation_basis="standalone",
                            reporting_scope="company_total_operations", comparability_cohort="example",
                            verified=True, metric="trade_receivables", unit="INR_crore", value=20,
                            period_start="2024-04-01", period_end="2025-03-31"),
            SimpleNamespace(company="Example", period="FY2025", consolidation_basis="standalone",
                            reporting_scope="company_total_operations", comparability_cohort="example",
                            verified=True, metric="revenue", unit="INR_crore", value=100,
                            period_start="2024-04-01", period_end="2025-03-31"),
        ]
        reference = {"company": "Example", "period": "FY2025", "basis": "standalone",
                     "reporting_scope": "company_total_operations", "comparability_cohort": "example",
                     "engine_metric": "receivable_days"}
        self.assertAlmostEqual(_engine_value(reference, rows), receivable_days(20, 100, 365))

    def test_duplicate_ledger_inputs_are_not_arbitrarily_selected(self):
        base = dict(company="Example", period="FY2025", consolidation_basis="standalone",
                    reporting_scope="company_total_operations", comparability_cohort="example",
                    verified=True, unit="INR_crore", period_start="2024-04-01", period_end="2025-03-31")
        rows = [
            SimpleNamespace(**base, metric="trade_receivables", value=20),
            SimpleNamespace(**base, metric="trade_receivables", value=21),
            SimpleNamespace(**base, metric="revenue", value=100),
        ]
        reference = {"company": "Example", "period": "FY2025", "basis": "standalone",
                     "reporting_scope": "company_total_operations", "comparability_cohort": "example",
                     "engine_metric": "receivable_days"}
        self.assertIsNone(_engine_value(reference, rows))

    def test_other_deterministic_formula_families_can_be_recomputed(self):
        base = dict(company="Example", consolidation_basis="standalone",
                    reporting_scope="company_total_operations", comparability_cohort="example",
                    verified=True, period_start="2024-04-01", period_end="2025-03-31")
        rows = [
            SimpleNamespace(**base, period="FY2024", metric="revenue", value=100, unit="INR_crore"),
            SimpleNamespace(**base, period="FY2025", metric="revenue", value=120, unit="INR_crore"),
            SimpleNamespace(**base, period="FY2025", metric="volume_growth", value=10, unit="pct"),
            SimpleNamespace(**base, period="FY2025", metric="operating_cash_flow", value=80, unit="INR_crore"),
            SimpleNamespace(**base, period="FY2025", metric="ebitda", value=100, unit="INR_crore"),
            SimpleNamespace(**base, period="FY2024", metric="gross_margin", value=30, unit="pct"),
            SimpleNamespace(**base, period="FY2025", metric="gross_margin", value=32, unit="pct"),
            SimpleNamespace(**base, period="FY2024", metric="input_cost_index", value=100, unit="index"),
            SimpleNamespace(**base, period="FY2025", metric="input_cost_index", value=110, unit="index"),
        ]
        shared = {"company": "Example", "basis": "standalone", "reporting_scope": "company_total_operations",
                  "comparability_cohort": "example", "period": "FY2025", "prior_period": "FY2024"}
        self.assertAlmostEqual(_engine_value({**shared, "engine_metric": "price_volume"}, rows), (1.2 / 1.1) - 1)
        self.assertAlmostEqual(_engine_value({**shared, "engine_metric": "cash_conversion"}, rows), 0.8)
        self.assertAlmostEqual(_engine_value({**shared, "engine_metric": "margin_vs_input_cost"}, rows), -8)


if __name__ == "__main__":
    unittest.main()
