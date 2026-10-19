import json
import unittest
from pathlib import Path


class HistoricalPeriodMetadataTests(unittest.TestCase):
    def read_ledger(self):
        ledger_path = Path(__file__).parents[1] / "data" / "ledger.jsonl"
        return [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_itc_verified_annual_rows_match_statement_fiscal_year(self):
        rows = self.read_ledger()
        rows = [row for row in rows if row.get("id") in {f"L{i:04d}" for i in range(45, 57)}]

        self.assertEqual(len(rows), 12)
        for row in rows:
            with self.subTest(ledger_id=row["id"]):
                fiscal_year = int(row["period"][2:])
                self.assertEqual(row["period_type"], "annual")
                self.assertEqual(row["period_start"], f"{fiscal_year - 1}-04-01")
                self.assertEqual(row["period_end"], f"{fiscal_year}-03-31")
                self.assertTrue(row["verified"])
                self.assertTrue(row["source_sha256"])
                self.assertIsInstance(row["doc_page"], int)

    def test_full_company_observations_share_scope_without_merging_cohorts(self):
        rows = self.read_ledger()
        comparable = [
            row for row in rows
            if row.get("comparability_cohort") in {
                "ITC_standalone_pre_demerger",
                "pre_demerger_standalone_FY2020_FY2025",
                "Britannia_standalone_FY2020_FY2025",
            }
        ]

        self.assertTrue(comparable)
        self.assertEqual({row["reporting_scope"] for row in comparable}, {"company_total_operations"})
        self.assertTrue(all(row["verified"] for row in comparable))

    def test_britannia_panel_has_six_verified_annual_periods_for_core_metrics(self):
        rows = [row for row in self.read_ledger()
                if row.get("company") == "Britannia Industries Limited"
                and row.get("comparability_cohort") == "Britannia_standalone_FY2020_FY2025"]
        self.assertEqual(len(rows), 18)
        for metric in ("revenue", "inventory", "trade_receivables"):
            metric_rows = [row for row in rows if row["metric"] == metric]
            with self.subTest(metric=metric):
                self.assertEqual({row["period"] for row in metric_rows},
                                 {f"FY{year}" for year in range(2020, 2026)})
                self.assertTrue(all(row["verified"] for row in metric_rows))


if __name__ == "__main__":
    unittest.main()
