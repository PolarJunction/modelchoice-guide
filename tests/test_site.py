import re
import tomllib
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
REFERRAL = "https://nano-gpt.com/r/MRpqWxhj"
CANONICAL = "https://modelgrove.dev/"


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

    def test_modelgrove_brand_and_canonical_domain(self):
        public_files = [
            self.text,
            (ROOT / "guides" / "nanogpt-codex-cli.html").read_text(encoding="utf-8"),
            (ROOT / "robots.txt").read_text(encoding="utf-8"),
            (ROOT / "sitemap.xml").read_text(encoding="utf-8"),
        ]
        joined = "\n".join(public_files)
        self.assertIn("ModelGrove", joined)
        self.assertIn(CANONICAL, joined)
        self.assertNotIn("ModelChoice", joined)
        self.assertNotIn("modelchoice-guide.netlify.app", joined)
        netlify = tomllib.loads((ROOT / "netlify.toml").read_text(encoding="utf-8"))
        redirects = netlify.get("redirects", [])
        self.assertIn(
            {
                "from": "https://modelchoice-guide.netlify.app/*",
                "to": "https://modelgrove.dev/:splat",
                "status": 301,
                "force": True,
            },
            redirects,
        )

    def test_codex_guide_is_current_and_secret_safe(self):
        guide = (ROOT / "guides" / "nanogpt-codex-cli.html").read_text(encoding="utf-8")
        escaped = guide.replace('"', '&quot;')
        self.assertGreaterEqual(escaped.count('wire_api = &quot;responses&quot;'), 2)
        self.assertIn("older examples using", guide)
        self.assertIn("No paid inference claimed", guide)
        self.assertIn('rel="sponsored nofollow noopener"', guide)
        fixture = '''model_provider = "nanogpt"
model = "openai/gpt-5.2"
[model_providers.nanogpt]
name = "NanoGPT"
base_url = "https://nano-gpt.com/api/v1"
env_key = "NANOGPT_API_KEY"
wire_api = "responses"
'''
        parsed = tomllib.loads(fixture)
        self.assertEqual(parsed["model_providers"]["nanogpt"]["wire_api"], "responses")


if __name__ == "__main__":
    unittest.main()
