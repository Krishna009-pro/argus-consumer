import unittest

from argus.peers import eligible_peer_panels
from argus.engine import make_dossier, _peer_company_names


def panel(company, *, cohort, scope="continuing_operations", basis="consolidated", currency="INR", period="FY2025", period_end=None):
    return {"company": company, "period_type": "annual", "currency": currency,
            "consolidation_basis": basis, "reporting_scope": scope,
            "comparability_cohort": cohort, "periods": [{"period": period, "period_end": period_end}]}


class PeerSelectionTests(unittest.TestCase):
    def test_multiple_compatible_cohorts_count_as_one_peer_company(self):
        self.assertEqual(_peer_company_names([
            {"company": "GCPL", "comparability_cohort": "pre-acquisition"},
            {"company": "GCPL", "comparability_cohort": "post-acquisition"},
            {"company": "Peer B", "comparability_cohort": "baseline"},
        ]), ["GCPL", "Peer B"])

    def test_company_local_cohort_names_do_not_block_comparable_peers(self):
        target = panel("Target Co", cohort="post_demerger_fy2026")
        peer = panel("Peer Co", cohort="FY2025-26_report_comparables")
        self.assertEqual(eligible_peer_panels(target, [target, peer]), [peer])

    def test_period_end_aligns_different_disclosed_labels(self):
        target = panel("Target Co", cohort="current", period="FY2026", period_end="2026-03-31")
        peer = panel("Peer Co", cohort="historical", period="FY2025-26", period_end="2026-03-31")
        self.assertEqual(eligible_peer_panels(target, [target, peer]), [peer])

    def test_peer_selection_requires_matching_scope_basis_currency_and_period(self):
        target = panel("Target Co", cohort="baseline")
        peers = [
            panel("Good", cohort="different-label"),
            panel("Wrong scope", cohort="x", scope="discontinued_operations"),
            panel("Wrong basis", cohort="x", basis="standalone"),
            panel("Wrong currency", cohort="x", currency="USD"),
            panel("Wrong period", cohort="x", period="FY2024"),
        ]
        self.assertEqual([p["company"] for p in eligible_peer_panels(target, [target, *peers])], ["Good"])

    def test_dossier_keeps_evidence_from_every_compatible_panel(self):
        def result(panel_id, period, ledger_id):
            return {"panel": {"period_type": "annual", "consolidation_basis": "consolidated",
                    "reporting_scope": "continuing_operations", "comparability_cohort": panel_id},
                "angles": {"price_volume": {"status": "abstained", "abstain_reason": "missing volume",
                    "periods": [period], "reported": [None], "ledger_ids_by_period": [[ledger_id]]}},
                "candidates": [], "tested_patterns": 0, "peer_companies": []}
        analysis = {"company": "Example Co", "panels": [result("cohort-a", "FY2024", "L0001"),
                    result("cohort-b", "FY2025", "L0002")], "rejected": []}
        dossier = make_dossier(analysis, [])
        self.assertEqual(dossier.evidence, ["L0001", "L0002"])
        self.assertEqual(len(dossier.timeline), 2)
        self.assertEqual(len(dossier.not_tested), 3)
        self.assertTrue(any("Peer-adjusted comparison" in reason for reason in dossier.not_tested))


if __name__ == "__main__":
    unittest.main()
