import tempfile, unittest, sys
from pathlib import Path
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch
from argus.ledger import EvidenceLedger
from argus.schemas import LedgerEntry
from argus.verify.claim_checker import check_claims

class ClaimCheckerTests(unittest.TestCase):
    def test_pdfplumber_fallback_extracts_and_checks_provenance(self):
        class Page:
            def extract_text(self):
                return "Standalone Balance Sheet\nParticulars Note As at 31st March, 2026 As at 31st March, 2025\nInventories 11 4,383 4,161"
        class Pdf:
            pages = [Page()]
            def __enter__(self): return self
            def __exit__(self, *args): return False
        def broken_reader(_): raise ValueError("unsupported object stream")
        fake_pypdf = SimpleNamespace(PdfReader=broken_reader)
        fake_pdfplumber = SimpleNamespace(open=lambda _: Pdf())
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.pdf"
            source.write_bytes(b"%PDF-test")
            with patch.dict(sys.modules, {"pypdf": fake_pypdf, "pdfplumber": fake_pdfplumber}):
                from argus.ingest.pdf_tables import extract
                from argus.ingest.source_text import snippet_is_cached
                candidates = extract(source)
                self.assertTrue(snippet_is_cached(source, "Inventories 11 4,383 4,161", 1))
        self.assertEqual([c["value"] for c in candidates], [4383.0, 4161.0])

    def test_pdf_extractor_uses_financial_columns_not_note_references(self):
        class Page:
            def __init__(self, text): self.text = text
            def extract_text(self):
                return self.text
        balance_sheet = "\n".join([
                    "Standalone Balance Sheet",
                    "Particulars Note As at 31st March, 2026 As at 31st March, 2025",
                    "Inventories  11  4,383  4,161",
                    "Trade receivables  12  3,037  3,450",
                    "The accompanying notes are an integral part of these financial statements",
                    "Narrative revenue increased 99 percent",
                ])
        profit_and_loss = "\n".join([
            "Dabur India Limited Integrated Annual Report 2025-26",
            "Standalone Statement of Profit and Loss",
            "For the year ended 31st March, 2026",
            "All amounts in INR crores, unless otherwise stated",
            "Particulars Note 31 March 2026 31 March 2025",
            "Revenue from operations 25 61,975 59,676",
        ])
        fake_pypdf = SimpleNamespace(PdfReader=lambda _: SimpleNamespace(pages=[Page(balance_sheet), Page(profit_and_loss)]))
        with patch.dict(sys.modules, {"pypdf": fake_pypdf}):
            from argus.ingest.pdf_tables import extract
            candidates = extract("unused.pdf")
        self.assertEqual([c["value"] for c in candidates],
                         [4383.0, 4161.0, 3037.0, 3450.0, 61975.0, 59676.0])
        self.assertNotIn(11.0, [c["value"] for c in candidates])
        self.assertNotIn(12.0, [c["value"] for c in candidates])
        self.assertTrue(all("Particulars Note" in c["column_header"] for c in candidates))
        self.assertEqual([c["period_header"] for c in candidates],
                         ["2026", "2025", "2026", "2025", "2026", "2025"])

    def test_source_snippet_and_hash_are_both_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "filing.txt"; source.write_text("Revenue from operations 123", encoding="utf-8")
            ledger = EvidenceLedger(root / "ledger.jsonl")
            entry = LedgerEntry(id="L0001", metric="revenue", value=123, unit="INR_cr", period="FY26", period_type="annual", currency="INR", consolidation_basis="consolidated", verified=True, verified_by="reviewer", verified_at=datetime.now(timezone.utc), source_url="https://example.org", source_type="filing", doc_page=2, snippet="Revenue from operations 123", source_sha256=ledger.sha256(source), retrieved_at=datetime.now(timezone.utc), cache_path=str(source), company="Example")
            ledger.append(entry)
            self.assertTrue(check_claims(ledger, ["L0001"])["passed"])
            source.write_text("Changed filing", encoding="utf-8")
            self.assertFalse(check_claims(ledger, ["L0001"])["passed"])

    def test_claim_rejects_missing_page_or_unsupported_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "filing.txt"; source.write_text("Revenue 123", encoding="utf-8")
            ledger = EvidenceLedger(root / "ledger.jsonl")
            entry = LedgerEntry(id="L0001", metric="revenue", value=999, unit="INR_cr", period="FY26", period_type="annual", currency="INR", consolidation_basis="consolidated", verified=True, verified_by="reviewer", verified_at=datetime.now(timezone.utc), source_url="https://example.org", source_type="filing", snippet="Revenue 123", source_sha256=ledger.sha256(source), retrieved_at=datetime.now(timezone.utc), cache_path=str(source), company="Example")
            with self.assertRaises(ValueError): ledger.append(entry)
