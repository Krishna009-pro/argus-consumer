import unittest
from argus.canary import generate, run

class CanaryTests(unittest.TestCase):
    def test_seeded_generation_is_deterministic_and_has_ground_truth(self):
        self.assertEqual(generate(44), generate(44))
        panels, truth = generate(44)
        self.assertEqual(len(panels), 40); self.assertEqual(len(truth), 40)
        self.assertEqual(sum(x["type"] is None for x in truth), 20)
        self.assertTrue(all(p["synthetic"] for p in panels))

    def test_metrics_are_measured_and_labeled_synthetic(self):
        result = run()
        self.assertTrue(result["synthetic"])
        self.assertIn("M07_canary_recall", result)
        self.assertIn("M08_canary_false_positive_rate", result)
