import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from argus.ledger import EvidenceLedger
from argus.ingest.local_import import _candidate, import_local, save_candidates, verify_candidate
from argus.panels import build_company_panels, derive_angle_series
from argus.schemas import LedgerEntry
from argus.engine import make_dossier


class PanelTests(unittest.TestCase):
    def test_candidate_ids_follow_claim_content_not_extraction_order(self):
        common = dict(company="Example", source_url="https://example.org/report", source_type="filing",
                      cache_path=Path("report.pdf"), digest="a" * 64,
                      metric="revenue", value=100.0, doc_page=4, snippet="Revenue 100")
        first = _candidate(1, **common)
        reordered = _candidate(9, **common)
        changed = _candidate(10, **{**common, "value": 101.0, "snippet": "Revenue 101"})
        self.assertEqual(first.id, reordered.id)
        self.assertNotEqual(first.id, changed.id)

    def test_dossier_retains_candidate_and_red_team_log_from_earlier_panel(self):
        earlier_panel = {
            "period_type": "annual", "consolidation_basis": "standalone",
            "reporting_scope": "continuing_operations", "comparability_cohort": "cohort-a",
        }
        later_panel = {**earlier_panel, "comparability_cohort": "cohort-b"}
        candidate = {
            "id": "Example:annual:FY25:receivable_days", "angles": ["receivable_days"],
            "gap_start_period": "FY23", "summary_numbers": {"persistence": 3.0},
            "gate": {"passed": False}, "state": "no_reliable_finding",
        }
        analysis = {
            "company": "Example", "rejected": [],
            "panels": [
                {"panel": earlier_panel, "angles": {"receivable_days": {"status": "abstained",
                    "periods": [], "red_team_tests": [{"test": "earlier", "outcome": "not_tested"}]}},
                 "candidates": [candidate], "tested_patterns": 1, "peer_companies": []},
                {"panel": later_panel, "angles": {"receivable_days": {"status": "abstained",
                    "periods": [], "red_team_tests": [{"test": "later", "outcome": "not_tested"}]}},
                 "candidates": [], "tested_patterns": 0, "peer_companies": []},
            ],
        }

        dossier = make_dossier(analysis, [])

        self.assertEqual(dossier.validation["generated_candidates"], [candidate])
        self.assertIn("detected", dossier.discovery)
        self.assertEqual([item["test"] for item in dossier.red_team_log], ["earlier", "later"])

    def _entry(self, ledger, source, idx, metric, value, period, unit="INR_cr", **kwargs):
        snippet = f"{metric} {value}"
        source.write_text(snippet, encoding="utf-8")
        return LedgerEntry(
            id=f"L{idx:04d}", metric=metric, value=value, unit=unit, period=period,
            period_type="annual", period_start=date(int(period[2:4]) + 2000, 4, 1),
            period_end=date(int(period[2:4]) + 2001, 3, 31), currency="INR",
            consolidation_basis="consolidated", verified=True, verified_by="reviewer",
            verified_at=datetime.now(timezone.utc), source_url="https://example.org/report",
            source_type="filing", doc_page=1, snippet=snippet, source_sha256=ledger.sha256(source),
            cache_path=str(source), company="Example", **kwargs)

    def test_derived_price_mix_uses_verified_revenue_and_volume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); ledger = EvidenceLedger(root / "ledger.jsonl"); entries = []; i = 0
            for year in range(19, 27):
                period = f"FY{year:02d}"
                i += 1; entries.append(self._entry(ledger, root / f"s{i}.txt", i, "revenue", 100 + (year - 19) * 10, period))
                i += 1; entries.append(self._entry(ledger, root / f"s{i}.txt", i, "volume_growth", 2.0, period, unit="percent"))
            panel = build_company_panels(entries, "Example")[0]
            result = derive_angle_series(panel)["price_volume"]
            self.assertEqual(result["status"], "tested")
            self.assertAlmostEqual(result["reported"][1], 1.10 / 1.02 - 1)
            self.assertTrue(result["ledger_ids_by_period"][1])

    def test_duplicate_metric_period_is_unavailable_instead_of_arbitrarily_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); ledger = EvidenceLedger(root / "ledger.jsonl")
            one = self._entry(ledger, root / "a.txt", 1, "revenue", 100, "FY26")
            two = self._entry(ledger, root / "b.txt", 2, "revenue", 101, "FY26")
            panel = build_company_panels([one, two], "Example")[0]
            self.assertIsNone(panel["metrics"]["revenue"][0])
            self.assertIn("revenue:FY26", panel["unavailable"])

    def test_partial_inventory_history_reports_period_count_not_missing_input(self):
        panel = {
            "periods": [
                {"period": "FY2024", "days": 366},
                {"period": "FY2025", "days": 365},
            ],
            "metrics": {"revenue": [100.0, 110.0], "inventory": [20.0, 22.0]},
            "ledger_ids": {"revenue": [["L1"], ["L2"]], "inventory": [["L3"], ["L4"]]},
            "units": {"revenue": "INR_crore", "inventory": "INR_crore"},
        }

        result = derive_angle_series(panel)["inventory_days"]

        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["abstain_reason"], "Fewer than six usable disclosed periods (2 of 2).")

    def test_missing_required_inputs_are_named_in_abstentions(self):
        panel = {
            "periods": [{"period": f"FY{year}", "days": 365} for year in range(2020, 2026)],
            "metrics": {"revenue": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]},
            "ledger_ids": {"revenue": [[f"L{i}"] for i in range(6)]},
            "units": {"revenue": "INR_crore"},
        }

        angles = derive_angle_series(panel)

        self.assertEqual(angles["price_volume"]["abstain_reason"],
                         "Matched revenue and disclosed volume-growth inputs are required.")
        self.assertEqual(angles["cash_conversion"]["abstain_reason"],
                         "Matched operating-cash-flow and EBITDA inputs are required.")
        self.assertEqual(angles["margin_vs_input_cost"]["abstain_reason"],
                         "Matched gross-margin and input-cost-index disclosures are required.")

    def test_local_csv_import_stays_unverified_until_human_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "observations.csv"
            source.write_text("metric,value,unit,period,snippet,page\nrevenue,100,INR_cr,FY26,Revenue 100,4\n", encoding="utf-8")
            cache, candidates = import_local(source, company="Example", source_url="https://example.org/report",
                cache_dir=root / "cache")
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0].status, "unverified")
            candidate_file = save_candidates(candidates, root / "candidates")
            ledger_path = root / "ledger.jsonl"
            entry = verify_candidate(candidate_file, candidates[0].id, verified_by="Reviewer",
                period="FY26", unit="INR_cr", period_type="annual", currency="INR",
                consolidation_basis="consolidated", ledger_path=ledger_path)
            self.assertEqual(entry.cache_path, str(cache))
            self.assertEqual(EvidenceLedger(ledger_path).verified_entries("Example")[0].id, entry.id)


if __name__ == "__main__": unittest.main()
