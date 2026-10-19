import unittest

from argus.search import extract_pdf_links, is_pdf_url


class PdfLinkDiscoveryTests(unittest.TestCase):
    def test_extracts_named_relative_and_absolute_pdf_links(self):
        html = """
        <a href="reports/annual-report.pdf">Annual Report 2025</a>
        <a href="https://cdn.example.com/accounts.pdf?download=1">Audited Accounts</a>
        <a href="/investors/">Investor page</a>
        <script src="/assets/app.js"></script>
        """
        links = extract_pdf_links(html, "https://company.example/reports/index.html")
        self.assertEqual(
            links,
            [
                {"title": "Annual Report 2025", "url": "https://company.example/reports/reports/annual-report.pdf"},
                {"title": "Audited Accounts", "url": "https://cdn.example.com/accounts.pdf?download=1"},
            ],
        )

    def test_pdf_url_detection_ignores_query_string(self):
        self.assertTrue(is_pdf_url("https://company.example/report.PDF?download=1"))
        self.assertFalse(is_pdf_url("https://company.example/reports/index.php"))

if __name__ == "__main__":
    unittest.main()
