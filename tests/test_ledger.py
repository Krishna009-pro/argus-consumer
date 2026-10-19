import tempfile, unittest
from pathlib import Path
from datetime import datetime, timezone
from argus.ledger import EvidenceLedger
from argus.schemas import LedgerEntry

class LedgerTests(unittest.TestCase):
    def test_round_trip_and_hash_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "source.txt"; source.write_text("Revenue 12", encoding="utf-8")
            ledger = EvidenceLedger(root / "ledger.jsonl")
            entry = LedgerEntry(id="L0001", metric="revenue", value=12, unit="INR_cr", period="FY26", period_type="annual", currency="INR", consolidation_basis="consolidated", verified=True, verified_by="reviewer", verified_at=datetime.now(timezone.utc), source_url="https://example.org/report", source_type="filing", doc_page=1, snippet="Revenue 12", source_sha256=ledger.sha256(source), retrieved_at=datetime.now(timezone.utc), cache_path=str(source), company="Example")
            ledger.append(entry)
            self.assertEqual(ledger.get("L0001").value, 12)
            self.assertTrue(ledger.verify(ledger.get("L0001")))
            source.write_text("Revenue 13", encoding="utf-8")
            self.assertFalse(ledger.verify(ledger.get("L0001")))
            with self.assertRaises(ValueError): ledger.append(entry)
