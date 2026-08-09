# ModelChoice

An independent, practical guide to NanoGPT's multi-model service, integrations and trade-offs.

## Referral disclosure

Links to NanoGPT invitations are referral links. Visitors receive NanoGPT's stated 5% discount on website queries; this project may receive referral credit from qualifying use. NanoGPT does not operate or endorse this guide.

## Quality checks

```bash
python3 -m unittest discover -s tests -v
npx --yes html-validate@9.7.1 index.html "guides/*.html"
node --input-type=module -e "import('./assets/calculator.mjs').then(({calculateSavings}) => console.log(calculateSavings(20)))"
```

Product and pricing claims were last checked against first-party NanoGPT pages on 9 August 2026.

## Guides

- [`guides/nanogpt-codex-cli.html`](guides/nanogpt-codex-cli.html) — current Responses API configuration, secret-safe checks, troubleshooting and rollback.
