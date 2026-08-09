import re
import tomllib
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

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
            self.assertTrue((ROOT / urlsplit(value).path).is_file(), value)

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
            (ROOT / "guides" / "nanogpt-claude-code.html").read_text(encoding="utf-8"),
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

    def test_homepage_has_story_led_conversion_funnel(self):
        self.assertIn('<body class="home">', self.text)
        self.assertIn('class="grove-scene"', self.text)
        self.assertIn('class="pixel-scene"', self.text)
        self.assertIn('class="portal"', self.text)
        self.assertGreaterEqual(self.text.count('class="model-spirit'), 4)
        self.assertIn('class="path-picker"', self.text)
        self.assertGreaterEqual(self.text.count('class="path-card'), 3)
        self.assertIn('class="offer-card', self.text)
        self.assertIn('class="mobile-cta"', self.text)
        self.assertIn("Referral · 5% qualifying web discount", self.text)
        self.assertIn('src="assets/experience.mjs"', self.text)

    def test_homepage_explains_offering_and_keeps_disclosure_proportionate(self):
        # The offering is explained in plain terms…
        self.assertIn("behind a single prepaid balance", self.text)
        self.assertIn("Pay per prompt", self.text)
        # …and the referral disclosure stays present but is stated once per
        # placement rather than shouted in the hero eyebrow.
        self.assertNotIn("Advertisement", self.text)
        self.assertIn("Referral link", self.text)
        self.assertIn("No subscription required", self.text)
        self.assertIn("$0.10 with crypto or $1 by card", self.text)
        self.assertNotIn("No subscriptions", self.text)
        self.assertNotIn("$0.10 by card or crypto", self.text)
        self.assertIn("How does this site make money?", self.text)

    def test_no_em_dashes_in_public_copy(self):
        public = [
            self.text,
            (ROOT / "guides" / "nanogpt-codex-cli.html").read_text(encoding="utf-8"),
            (ROOT / "guides" / "nanogpt-claude-code.html").read_text(encoding="utf-8"),
            (ROOT / "assets" / "styles.css").read_text(encoding="utf-8"),
        ]
        for content in public:
            self.assertNotIn("—", content)

    def test_pixel_art_carried_through_page(self):
        self.assertIn('class="pixel-logo"', self.text)
        self.assertGreaterEqual(self.text.count('class="pixel-icon'), 6)
        self.assertGreaterEqual(self.text.count('class="pixel-mono"'), 6)
        self.assertIn('class="footer-parade"', self.text)
        self.assertGreaterEqual(self.text.count('class="parade-sprite'), 14)
        for guide in ("nanogpt-codex-cli.html", "nanogpt-claude-code.html"):
            self.assertIn('class="pixel-logo"', (ROOT / "guides" / guide).read_text(encoding="utf-8"))

    def test_motion_is_progressive_and_respects_user_preference(self):
        script = (ROOT / "assets" / "experience.mjs").read_text(encoding="utf-8")
        styles = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("IntersectionObserver", script)
        self.assertIn("try {", script)
        self.assertIn("catch", script)
        self.assertIn("revealEverything();", script)
        self.assertIn('window.addEventListener("resize", updateScrollState', script)
        self.assertIn("Math.max(0, Math.min(", script)
        self.assertIn("addListener", script)
        self.assertIn("prefers-reduced-motion", script)
        self.assertIn("mobileCta", script)
        self.assertIn('classList.toggle("is-active"', script)
        self.assertIn("mobileCta.blur()", script)
        self.assertIn(".mobile-cta.is-active", styles)
        self.assertIn("visibility: hidden", styles)
        self.assertIn("visibility: visible", styles)
        self.assertNotIn("visibility 0s linear .25s", styles)
        self.assertIn("@media (prefers-reduced-motion: reduce)", styles)
        self.assertIn("scroll-behavior: auto", styles)
        self.assertNotIn("scroll-behaviour", styles)

    def test_responsive_hero_avoids_overflow_prone_layout(self):
        styles = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
        self.assertNotIn("minmax(520px", styles)
        self.assertNotIn("margin: -100px -90px", styles)
        self.assertNotIn("width: 133%", styles)
        self.assertIn("@media (max-width: 1100px)", styles)
        self.assertIn("@media (max-width: 800px)", styles)
        self.assertIn(".hero-copy .button", styles)
        self.assertIn("white-space: nowrap", styles)

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

    def test_claude_code_guide_separates_provider_and_mcp(self):
        guide = (ROOT / "guides" / "nanogpt-claude-code.html").read_text(encoding="utf-8")
        self.assertIn("model provider or MCP tools?", guide)
        self.assertIn("it does not switch the model powering Claude Code", guide)
        self.assertIn("ANTHROPIC_AUTH_TOKEN", guide)
        self.assertIn("NANOGPT_API_KEY", guide)
        self.assertIn("No paid inference claimed", guide)
        self.assertIn('rel="sponsored nofollow noopener"', guide)
        fixture = '''{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "paste-your-key-locally",
    "ANTHROPIC_BASE_URL": "https://nano-gpt.com/api/v1"
  }
}'''
        import json
        parsed = json.loads(fixture)
        self.assertEqual(parsed["env"]["ANTHROPIC_BASE_URL"], "https://nano-gpt.com/api/v1")


if __name__ == "__main__":
    unittest.main()
