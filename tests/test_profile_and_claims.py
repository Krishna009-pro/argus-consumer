import tempfile, unittest
from pathlib import Path
from argus.profile import profile_business, applicable_angles

class ProfileTests(unittest.TestCase):
    def test_unknown_profile_is_not_invented_and_retail_skips_distributor_metrics(self):
        unknown = profile_business({})
        self.assertIsNone(unknown.distributor_led)
        self.assertFalse(applicable_angles(unknown)["distributor_metrics"][0])
        own_store = profile_business({"own_store_retail": True, "distributor_led": False})
        self.assertTrue(applicable_angles(own_store)["store_economics"][0])
        self.assertFalse(applicable_angles(own_store)["distributor_metrics"][0])
