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

    def test_marico_standalone_panel_has_six_verified_periods_and_recased_fy2020(self):
        rows = [row for row in self.read_ledger()
                if row.get("company") == "Marico Limited"
                and row.get("comparability_cohort") == "Marico_standalone_FY2020_FY2025_recast_FY2020"]
        self.assertEqual(len(rows), 18)
        for metric in ("revenue", "inventory", "trade_receivables"):
            metric_rows = [row for row in rows if row["metric"] == metric]
            with self.subTest(metric=metric):
                self.assertEqual({row["period"] for row in metric_rows},
                                 {f"FY{year}" for year in range(2020, 2026)})
                self.assertTrue(all(row["verified"] for row in metric_rows))
                self.assertTrue(all(row["consolidation_basis"] == "standalone" for row in metric_rows))
                self.assertTrue(all(row["source_sha256"] and row["doc_page"] for row in metric_rows))
        fy2020 = [row for row in rows if row["period"] == "FY2020"]
        self.assertEqual(len(fy2020), 3)
        self.assertTrue(all("marked Recast" in row["comparability_note"] for row in fy2020))

    def test_dabur_standalone_panel_has_six_verified_periods_with_source_provenance(self):
        rows = [row for row in self.read_ledger()
                if row.get("company") == "Dabur India Limited"
                and row.get("comparability_cohort") == "Dabur_standalone_FY2020_FY2025"]
        self.assertEqual(len(rows), 18)
        expected_values = {
            "revenue": [6309.80, 7184.73, 8179.50, 8684.35, 9135.60, 9070.71],
            "inventory": [809.14, 1114.16, 1237.96, 1223.77, 1149.88, 1288.07],
            "trade_receivables": [379.63, 281.24, 454.55, 561.18, 719.21, 600.58],
        }
        for metric, values in expected_values.items():
            metric_rows = sorted((row for row in rows if row["metric"] == metric),
                                 key=lambda row: row["period"])
            with self.subTest(metric=metric):
                self.assertEqual([row["period"] for row in metric_rows],
                                 [f"FY{year}" for year in range(2020, 2026)])
                self.assertEqual([row["value"] for row in metric_rows], values)
                for row in metric_rows:
                    self.assertTrue(row["verified"])
                    self.assertEqual(row["consolidation_basis"], "standalone")
                    self.assertEqual(row["unit"], "INR_crore")
                    self.assertEqual(row["period_type"], "annual")
                    self.assertEqual(row["reporting_scope"], "company_total_operations")
                    self.assertTrue(row["source_sha256"])
                    self.assertIsInstance(row["doc_page"], int)
                    self.assertTrue(row["snippet"])


if __name__ == "__main__":
    unittest.main()
