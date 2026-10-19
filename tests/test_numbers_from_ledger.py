"""R2/R3: narrative numeric claims are traceable; model hypotheses are qualitative."""
import re, unittest
from argus.report.dossier import abstention_dossier, render

class NumericGroundingTests(unittest.TestCase):
    def test_no_numeric_hypotheses_and_numbered_claims_name_a_ledger_id(self):
        dossier = abstention_dossier("Example Consumer")
        dossier.numbers = {"revenue FY26 [L0001]": 120.0}
        rendered = render(dossier)
        for key in dossier.numbers:
            self.assertRegex(key, r"\[L\d{4}\]")
        for hypothesis in dossier.hypotheses:
            self.assertIsNone(re.search(r"\d", hypothesis))
        self.assertIn("revenue FY26 [L0001]: 120.0", rendered)
        self.assertNotIn("No verified numeric claims", rendered)

    def test_abstention_dossier_has_no_numeric_claim_tokens(self):
        rendered = render(abstention_dossier("Example Consumer"))
        self.assertIsNone(re.search(r"\d", rendered))

    def test_unlinked_numeric_claim_is_rejected(self):
        dossier = abstention_dossier("Example Consumer")
        dossier.numbers = {"revenue FY26": 120.0}
        self.assertFalse(all(re.search(r"\[L\d{4}\]", claim) for claim in dossier.numbers))
