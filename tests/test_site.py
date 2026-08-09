import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
REFERRAL = "https://nano-gpt.com/r/MRpqWxhj"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in {"a", "link", "script"}:
            self.links.append((tag, dict(attrs)))


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HTML.read_text(encoding="utf-8")
        cls.parser = LinkParser()
        cls.parser.feed(cls.text)

    def test_referral_links_are_disclosed_and_marked_sponsored(self):
        links = [attrs for tag, attrs in self.parser.links if tag == "a" and attrs.get("href") == REFERRAL]
        self.assertGreaterEqual(len(links), 3)
        for link in links:
            rel = set(link.get("rel", "").split())
            self.assertTrue({"sponsored", "nofollow", "noopener"}.issubset(rel))
        self.assertIn("Referral links may earn this site credit", self.text)

    def test_public_copy_does_not_claim_unverified_referrer_percentage(self):
        self.assertNotRegex(self.text, re.compile(r"10%.*(?:referr|earn|credit)", re.I | re.S))

    def test_local_assets_exist(self):
        local = []
        for _, attrs in self.parser.links:
            value = attrs.get("href") or attrs.get("src")
            if value and not value.startswith(("http:", "https:", "#", "mailto:")):
                local.append(value)
        self.assertTrue(local)
        for value in local:
            self.assertTrue((ROOT / value).is_file(), value)

    def test_no_secrets_or_analytics(self):
        forbidden = ["NOVA_" + "NANOGPT_API_KEY", "x-" + "api-key", "google-analytics", "plausible.io", "posthog"]
        for token in forbidden:
            self.assertNotIn(token, self.text)

    def test_accessibility_basics(self):
        self.assertIn('lang="en-GB"', self.text)
        self.assertIn('href="#main"', self.text)
        self.assertIn('id="main"', self.text)
        self.assertIn('aria-live="polite"', self.text)
        self.assertEqual(self.text.count("<h1>"), 1)


if __name__ == "__main__":
    unittest.main()
