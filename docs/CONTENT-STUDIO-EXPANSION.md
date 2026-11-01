# RESCU Content Factory — expansion: eight campaigns + social previews

Status: **working local preview; not deployed to RESCU.life**.

## What is included

- Eight public-source campaign specifications in `examples/2026-rescu-eight-campaigns.json`.
- Offline batch builder `rescu_growth/content_studio.py`.
- Each campaign gets a mobile-friendly article draft, Instagram caption, 9:16 reel storyboard, clinical review checklist, 1080x1350 post cover, and 1080x1920 Story cover.
- A local HTML dashboard (`index.html`) links to each draft.
- `content-calendar.csv` provides a proposed four-week, two-post-per-week schedule. No events are scheduled.
- `campaign-links.csv` holds UTM-tagged booking links. `measurement-template.csv` has blank metrics (not fabricated results).
- Python tests and GitHub Actions CI validate the batch without contacting any paid APIs or publishing.

## Run on an ordinary computer

Python 3.11 or newer:

```bash
pip install Pillow
python -m unittest discover -s tests -v
python -m rescu_growth.content_studio \
  --manifest examples/2026-rescu-eight-campaigns.json \
  --output-dir output/rescu-eight
```

Open `output/rescu-eight/index.html` in a local browser. Without Pillow, add `--no-images` to create text, CSV and storyboard outputs; the dashboard is only generated when PNGs are generated. For silent MP4 drafts, install free FFmpeg and use `python -m rescu_growth.reel_render` on a chosen storyboard.

## The eight topics

1. First HBOT visit — chamber, introductory appointment, and screening questions.
2. TriLift demo — early-adopter provider and what to ask about components.
3. Six-week Skin Plan — components, minimally invasive RF microneedling, and safe spacing.
4. Complimentary RESCU Reset — what is included, new-guest eligibility.
5. Emsella — pelvic floor consultation questions.
6. Corporate wellness — discussion starter for Westchester teams.
7. Emsculpt NEO — body-contouring consultation expectations.
8. Ozone consultation — evidence limitations and screening.

They link to existing RESCU material. Editorial review should decide whether a standalone new journal article is genuinely useful and sufficiently different from current on-site guides; **do not publish duplicate SEO pages**.

## Guardrails

- No platform posting, emailing, auto-scheduling, patient database or vendor API integration.
- No patient data. Avoid patient photos, synthesized medical results, audio cloning, or unapproved testimonials.
- Covers show text-based branding, **not** the registered official RESCU quadrants logo, which must be supplied and authorized separately.
- Every medical claim, price, citation and current offer must be checked by a physician/editor. The presence of a URL is **not** proof that it supports a claim.
- Source statements are for editor verification, not medical evidence. Where appropriate, add current primary medical references and clear evidence limitations.
- New URLs exist only in draft form; canonical, links, accessibility and sitemap must be reviewed before production.
- No third-party GitHub app is installed. This is a dependency-light local implementation of the most useful functions.

## Optional next steps

- Export selected storyboard to HyperFrames and try HTML motion rendering locally once the tool is installed and security-reviewed.
- Add actual voiceover and verified captions only after the original recording has been approved.
- Use aggregate booking completion to measure which content brings real consultations.

**GitHub:** Draft Pull Request #1 in Rescu1021/rescu-growth-engine. GitHub Actions checks are configured to run offline tests on changes and do not deploy.
