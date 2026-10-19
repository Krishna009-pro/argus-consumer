import unittest
from argus.metrics import price_mix_growth, receivable_days, inventory_days, cash_conversion, expected_range, longest_recent_run
from argus.angles.price_volume import compute

class MetricTests(unittest.TestCase):
    def test_hand_calculated_metric_formulas(self):
        self.assertAlmostEqual(price_mix_growth(.21, .10), .10)
        self.assertAlmostEqual(receivable_days(20, 100, 180), 36)
        self.assertAlmostEqual(inventory_days(10, 100, 180), 18)
        self.assertAlmostEqual(cash_conversion(25, 50), .5)

    def test_missing_inputs_abstain(self):
        self.assertIsNone(price_mix_growth(.1, None))
        self.assertEqual(compute(.1, None)["status"], "abstained")
        self.assertIsNone(receivable_days(None, 100, 90))
        self.assertIsNone(cash_conversion(None, 10))

    def test_expected_range_excludes_latest_two(self):
        result = expected_range([1, 1, 1, 1, 90, 100])
        self.assertEqual(result, (1, 1, 0))
        self.assertIsNone(expected_range([1, 2, 3, 4, 5]))
        self.assertEqual(longest_recent_run([False, True, True, True]), 3)
