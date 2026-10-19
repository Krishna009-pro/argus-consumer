import tempfile, unittest
from pathlib import Path
from argus.agents.hypothesis import plan_queries
from argus.validation_gate import validate
from argus.verify.score import calculate

class AgentGateTests(unittest.TestCase):
    def test_skeptic_budget_is_at_least_thirty_percent(self):
        queries = plan_queries({"id": "candidate", "angles": ["working_capital"]})
        self.assertGreaterEqual(sum(q["tag"] == "disconfirming" for q in queries) / len(queries), .30)

    def test_each_gate_condition_is_enforced(self):
        baseline = dict(persistence=4, peer_adjusted_deviation=3.0, hashes_valid=True, benign_gap_share=.2, patterns_tested=1, source_layers=3)
        self.assertTrue(validate(**baseline)["passed"])
        failures = [
            {**baseline, "persistence": 2}, {**baseline, "peer_adjusted_deviation": 1.4},
            {**baseline, "hashes_valid": False}, {**baseline, "benign_gap_share": .61},
            {**baseline, "peer_adjusted_deviation": 1.5, "patterns_tested": 16},
            {**baseline, "source_layers": 1},
        ]
        for case in failures:
            with self.subTest(case=case): self.assertFalse(validate(**case)["passed"])

    def test_evidence_score_keeps_business_importance_out(self):
        score = calculate(4, 5, 2, 3, 3, .8)
        self.assertEqual(score.label, "Strong")
        self.assertEqual(set(score.components), {"persistence", "magnitude", "peer_adjusted", "independent_sources", "robustness"})
