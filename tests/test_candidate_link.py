import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from argus.ingest.local_import import link_candidate
from argus.ledger import EvidenceLedger
from argus.schemas import LedgerEntry, ObservationCandidate


class CandidateLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "report.pdf"
        self.source.write_bytes(b"%PDF test source")
        self.digest = EvidenceLedger.sha256(self.source)
        self.ledger_path = self.root / "ledger.jsonl"
        reviewed = LedgerEntry(
            id="L0001", metric="inventory", value=1235, unit="INR_crore", period="FY2025",
            source_url="https://example.com/report.pdf", source_type="filing", doc_page=4,
            snippet="Inventories 9 1,235 1,336", source_sha256=self.digest,
            cache_path=str(self.source), company="Example Limited", period_type="annual",
            period_start="2024-04-01", period_end="2025-03-31", currency="INR",
            consolidation_basis="consolidated", verified=True, verified_by="Reviewer",
            verified_at=datetime.now(timezone.utc), reporting_scope="company_total_operations",
            comparability_cohort="example_consolidated",
        )
        self.ledger_path.write_text(reviewed.model_dump_json() + "\n", encoding="utf-8")
        self.candidate_path = self.root / "candidates.json"
        self.write_candidate(value=1235)

    def tearDown(self):
        self.temp.cleanup()

    def write_candidate(self, value):
        candidate = ObservationCandidate(
            id="C-1", metric="inventory", value=value, source_url="https://example.com/report.pdf",
            source_type="filing", doc_page=4, snippet="Inventories 9 1,235 1,336",
            source_sha256=self.digest, cache_path=str(self.source), company="Example Limited",
        )
        self.candidate_path.write_text(json.dumps([candidate.model_dump(mode="json")]), encoding="utf-8")

    def test_exact_candidate_links_to_existing_review_without_duplicate_ledger_row(self):
        with patch("argus.ingest.source_text.snippet_is_cached", return_value=True), \
             patch("argus.ingest.source_text.snippet_contains_value", return_value=True):
            linked = link_candidate(self.candidate_path, "C-1", "L0001", ledger_path=self.ledger_path)

        self.assertEqual(linked.status, "verified")
        self.assertEqual(linked.ledger_entry_id, "L0001")
        self.assertEqual(linked.period, "FY2025")
        self.assertEqual(len(EvidenceLedger(self.ledger_path).entries()), 1)

    def test_value_mismatch_cannot_be_linked_or_change_candidate(self):
        self.write_candidate(value=1234)

        with patch("argus.ingest.source_text.snippet_is_cached", return_value=True), \
             patch("argus.ingest.source_text.snippet_contains_value", return_value=True):
            with self.assertRaisesRegex(ValueError, "value"):
                link_candidate(self.candidate_path, "C-1", "L0001", ledger_path=self.ledger_path)

        remaining = json.loads(self.candidate_path.read_text(encoding="utf-8"))[0]
        self.assertEqual(remaining["status"], "unverified")
        self.assertIsNone(remaining["ledger_entry_id"])
        self.assertEqual(len(EvidenceLedger(self.ledger_path).entries()), 1)


if __name__ == "__main__":
    unittest.main()
