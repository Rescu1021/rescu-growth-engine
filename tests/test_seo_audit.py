"""Offline tests for the public-site SEO audit (no external requests)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "seo"))
from site_audit import inspect_html, normalized, render, Page  # noqa: E402

BASE = "https://rescu.life/"


class TestSEOAudit(unittest.TestCase):
    def test_good_metadata_and_schema(self):
        description = "Rescu Wellness offers physician-led wellness services, clinical screening and individualized recovery and aesthetics consultations in Scarsdale, New York."
        markup = f"""
        <html><head>
          <title>Physician-Led Wellness in Scarsdale NY | RESCU</title>
          <meta name="description" content="{description}">
          <link rel="canonical" href="https://rescu.life/">
          <script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalBusiness"}}</script>
        </head><body><h1>Welcome to RESCU</h1>
        <p>111 Brook Street Scarsdale NY 10583. Call 914-401-8552.</p>
        </body></html>"""
        page = inspect_html(BASE, markup)
        self.assertEqual(page.issues, [])
        self.assertEqual(page.schemas, ["MedicalBusiness"])
        self.assertEqual(page.h1s, ["Welcome to RESCU"])

    def test_missing_and_noindex(self):
        page = inspect_html(BASE, '<html><head><meta name="robots" content="noindex,follow"></head><body><h1>One</h1><h1>Two</h1></body></html>')
        self.assertTrue(any("Missing title" in x for x in page.issues))
        self.assertTrue(any("Missing meta description" in x for x in page.issues))
        self.assertTrue(any("one H1" in x for x in page.issues))
        self.assertTrue(any("noindex" in x for x in page.issues))

    def test_canonical_redirect_suggestion(self):
        markup = '<title>Example</title><meta name="description" content="' + ("a" * 100) + '"><link rel="canonical" href="/other"><h1>Example</h1>'
        page = inspect_html("https://rescu.life/hbot", markup)
        self.assertIn("Canonical points elsewhere: https://rescu.life/other", page.issues)

    def test_normalized_slashes(self):
        self.assertEqual(normalized("https://RESCU.life/hbot/"), normalized("https://rescu.life/hbot"))

    def test_report_escapes_table_separators(self):
        page = Page(url="https://rescu.life/hbot", title="HBOT | RESCU", issues=["Foo | Bar"])
        report = render([page], [])
        self.assertIn("HBOT / RESCU", report)
        self.assertIn("Foo / Bar", report)


if __name__ == "__main__":
    unittest.main()
