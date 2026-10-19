import unittest
from types import SimpleNamespace

from argus.cli import _candidate_review_summary


class CandidateReviewSummaryTests(unittest.TestCase):
    def test_reused_verified_and_ambiguous_candidates_are_counted_separately(self):
        candidates = [
            SimpleNamespace(status="verified"),
            SimpleNamespace(status="verified"),
            SimpleNamespace(status="ambiguous"),
        ]

        summary = _candidate_review_summary(candidates)

        self.assertEqual(summary["status"], "candidates_present_review_required")
        self.assertEqual(summary["verified_candidate_count"], 2)
        self.assertEqual(summary["unresolved_candidate_count"], 1)
        self.assertEqual(summary["candidate_status_counts"], {
            "verified": 2, "unverified": 0, "ambiguous": 1, "missing": 0,
        })

    def test_empty_candidate_set_is_reported(self):
        self.assertEqual(_candidate_review_summary([])["status"], "no_candidates_extracted")


if __name__ == "__main__":
    unittest.main()
