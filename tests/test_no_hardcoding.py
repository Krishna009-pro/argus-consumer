"""R1: source logic must not contain company-specific identifiers."""
import unittest
from pathlib import Path

def find_company_identifiers(source: str, identifiers: tuple[str, ...]) -> list[str]:
    upper = source.upper()
    return [identifier for identifier in identifiers if identifier in upper]

class NoHardcodingTests(unittest.TestCase):
    def test_company_names_and_tickers_absent_from_source(self):
        forbidden = ("RELIANCE", "HINDUNILVR", "ITC", "NESTLEIND", "TATACONSUM", "BRITANNIA", "DABUR", "MARICO")
        source_root = Path(__file__).resolve().parents[1] / "src"
        for path in source_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name): self.assertEqual(find_company_identifiers(text, forbidden), [])

    def test_guard_detects_a_deliberate_ticker_violation(self):
        self.assertEqual(find_company_identifiers("if ticker == 'RELIANCE':", ("RELIANCE",)), ["RELIANCE"])
