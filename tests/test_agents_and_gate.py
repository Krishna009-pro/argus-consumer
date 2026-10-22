import tempfile, unittest
from pathlib import Path
from argus.agents.hypothesis import plan_queries
from argus.agents.redteam import benign_gap_share, challenge
from argus.ledger import EvidenceLedger
from argus.validation_gate import validate
from argus.verify.score import calculate

class AgentGateTests(unittest.TestCase):
    def test_skeptic_budget_is_at_least_thirty_percent(self):
        queries = plan_queries({"id": "candidate", "angles": ["working_capital"]})
        self.assertGreaterEqual(sum(q["tag"] == "disconfirming" for q in queries) / len(queries), .30)

    def test_each_gate_condition_is_enforced(self):
        baseline = dict(persistence=4, peer_adjusted_deviation=3.0, hashes_valid=True, benign_gap_share=.2, patterns_tested=1, source_layers=3)
        self.assertTrue(validate(**baseline)["passed"])
        self.assertTrue(validate(**{**baseline, "benign_gap_share": None})["passed"])
        failures = [
            {**baseline, "persistence": 0}, {**baseline, "peer_adjusted_deviation": 1.4},
            {**baseline, "hashes_valid": False}, {**baseline, "benign_gap_share": .61},
            {**baseline, "peer_adjusted_deviation": 1.5, "patterns_tested": 16},
            {**baseline, "source_layers": 0},
        ]
        for case in failures:
            with self.subTest(case=case): self.assertFalse(validate(**case)["passed"])

    def test_evidence_score_keeps_business_importance_out(self):
        score = calculate(4, 5, 2, 3, 3, .8)
        self.assertEqual(score.label, "Strong")
        self.assertEqual(set(score.components), {"persistence", "magnitude", "peer_adjusted", "independent_sources", "robustness"})

    def test_red_team_missing_sources_remain_not_tested(self):
        results = challenge({"summary_numbers": {"gap_magnitude": 100}})
        self.assertEqual(len(results), 7)
        self.assertTrue(all(row["outcome"] == "not_tested" for row in results))
        self.assertTrue(all(row["benign_gap_share"] is None for row in results))

    def test_red_team_requires_valid_hash_review_and_exact_cached_snippet(self):
        with tempfile.TemporaryDirectory() as folder:
            source_path = Path(folder) / "source.txt"
            source_path.write_text("Reviewed note: seasonal impact was INR 25 crore.", encoding="utf-8")
            source = {
                "source_url": "https://example.test/report.pdf",
                "cache_path": str(source_path),
                "source_sha256": EvidenceLedger.sha256(source_path),
                "locator": "Reviewed note",
                "snippet": "Reviewed note: seasonal impact was INR 25 crore.",
                "review_status": "verified",
                "reviewed_by": "test reviewer",
            }
            valid = {"seasonality": {"outcome": "supported", "reason": "Test fixture", "sources": [source],
                                     "benign_explained_amount": 25, "amount_unit": "days"}}
            rows = challenge({"summary_numbers": {"gap_magnitude": 100, "gap_unit": "days"}}, valid)
            seasonal = rows[0]
            self.assertEqual(seasonal["outcome"], "supported")
            self.assertEqual(seasonal["benign_gap_share"], .25)
            self.assertEqual(seasonal["quantification_status"], "source_supported")

            tampered = {"seasonality": {**valid["seasonality"], "sources": [{**source, "source_sha256": "0" * 64}]}}
            self.assertEqual(challenge({"summary_numbers": {"gap_magnitude": 100, "gap_unit": "days"}}, tampered)[0]["outcome"], "not_tested")
            malformed = {"seasonality": {**valid["seasonality"], "sources": [{**source, "source_url": None}]}}
            self.assertEqual(challenge({"summary_numbers": {"gap_magnitude": 100, "gap_unit": "days"}}, malformed)[0]["outcome"], "not_tested")
            mismatch = challenge({"summary_numbers": {"gap_magnitude": 100, "gap_unit": "days"}},
                                 {"seasonality": {**valid["seasonality"], "amount_unit": "INR_crore"}})[0]
            self.assertIsNone(mismatch["benign_gap_share"])

    def test_benign_share_rejects_missing_invalid_or_out_of_range_amounts(self):
        units = {"amount_unit": "days", "gap_unit": "days"}
        self.assertEqual(benign_gap_share(explained_amount=25, gap_magnitude=100, **units), .25)
        self.assertIsNone(benign_gap_share(explained_amount=101, gap_magnitude=100, **units))
        self.assertIsNone(benign_gap_share(explained_amount=0, gap_magnitude=0, **units))
        self.assertIsNone(benign_gap_share(explained_amount="unknown", gap_magnitude=100, **units))
        self.assertIsNone(benign_gap_share(explained_amount=25, gap_magnitude=100,
                                          amount_unit="INR_crore", gap_unit="days"))
