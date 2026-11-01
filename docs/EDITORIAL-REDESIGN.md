# RESCU editorial graphics — Pinterest-informed, official logo

## What changed

The generic geometric cover series has been replaced in the delivered preview pack by original magazine-style editorial layouts with treatment-specific imagery. The authentic **four-quadrant categories RESCU logo** is used intact, from the user's connected Google Drive.

- Official source: `quad logo with categories.png` (Drive ID `15CsvZLisJkUoXgTVVHiMF640Eoj9DrnO`).
- Do not draw, invent, recreate, reshape or recolor the RESCU mark.
- The image assets supplied with the preview pack are **AI-generated illustrative concepts**, not real Rescu clinic equipment, staff, patients or outcomes. Every image carries a concept disclaimer.
- Reference inspiration: [Pinterest 2026 trend report](https://business.pinterest.com/pdf/pinterest-predicts/2026-trend-report/) and [Pinterest creative best-practices guide](https://business.pinterest.com/pdf/holiday-playbook-2025); original interpretation of mobile-first editorial photography, warm contrast, and high-readability typography.
- Avoid duplicating or reproducing a Pinterest creator's design. There is no verifiable objective "most popular" Pinterest poster in the research.

## Rebuild the eight visuals locally

The photo concept sheet and official logo belong to the owner's provided asset bundle, **not this public repo**. Keep any supplied patient/employee photography separate from the content generator.

```bash
python -m pip install Pillow
python -m rescu_growth.content_studio \
  --manifest examples/2026-rescu-eight-campaigns.json \
  --output-dir output/editorial \
  --logo-path /path/to/official-rescu-quad-logo.png \
  --photo-sheet /path/to/original-4-by-2-photo-concept-sheet.png
```

This creates 1080x1350 post covers and 1080x1920 Story covers with the supplied exact logo, and the original batch HTML dashboard, article drafts, captions and reel storyboard files. If either external asset is not supplied, the explicit editorial renderer does not run. The fallback legacy cover generator is retained only for backward compatibility, and should not be used in newly approved campaign assets.

## Publishing gate

1. Verify clinical and marketing statements, published treatment eligibility, contraindications, prices, and booking links.
2. For any visual that depicts a clinic, staff or equipment, preserve the **illustrative** disclaimer until replaced with consented genuine RESCU material.
3. Keep the official quadrants mark exactly intact, including the category labels.
4. Review Pinterest inspiration for patterns only; no copying or trademark appropriation.
5. Confirm social safe zones and quality on a phone. Do not assume any uploaded images are real RESCU results.
6. Human approves everything before publishing. This code does not deploy, schedule posts, or modify live Cloudflare routes.

No paid design subscription or AI API is required to run the code with local photos and the original logo.