# RESCU video content enhancements — review-only integration

**Status:** Proposed video production workflow on a feature branch, **not deployed to Rescu.life**. No new production bindings, paid services, AI voice calls, third-party software installations, or automated publishing.

## Why these two projects are relevant

- [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit): MIT-licensed reference for professional motion-design principles and independent visual/audio quality review. Its ideas informed this **original** lightweight offline checklist and production direction. The toolkit itself is not vendored.
- [Vincentwei1021/anything2explainer](https://github.com/Vincentwei1021/anything2explainer): illustrates the usefulness of chapters, storyboards, captions and a recorded voiceover. **PolyForm Noncommercial 1.0.0:** commercial use of that toolkit requires permission from its author. No code, templates, fonts, assets or executables from it are copied or installed here. This repository's planning system is independently implemented.

Remotion and any music, imagery, voice or video model require their own commercial-use review before adoption.

## What is implemented

Each existing valid RESCU campaign now generates these **draft** files alongside its landing page, article, caption, branded covers and silent reel storyboard:

- `video-production.json` — four timed scenes, visual framing and motion guidance, source register, chapters, brand controls, website handoff requirements.
- `voiceover-draft.txt` — narration taken from the campaign's existing medically reviewable copy; **not an audio file**.
- `captions-draft.vtt` — rough captions aligned to **scene boundaries, not an actual recording**. Requires human synchronization before use.
- `video-quality-review.json` — automatic timing/pacing flags and blocked human review gates.

No claims, pricing, patient outcomes, staff identities or treatment benefits are generated from model inference; the source links supplied in campaigns must still be independently verified by the clinical editor.

## Use locally

```sh
python -m pip install . Pillow
python -m unittest discover -s tests -v
python -m rescu_growth.content_studio \
  --manifest examples/2026-rescu-eight-campaigns.json \
  --output-dir output/rescu-eight
```

Find a video plan under `output/rescu-eight/campaigns/<slug>/`. Open the local `index.html` dashboard to review each pack. With `--no-images`, all text/video planning assets are still generated, but no dashboard or cover images are generated.

Optional silent video preview (no narration or soundtrack):

```sh
python -m rescu_growth.reel_render \
  --storyboard output/rescu-eight/campaigns/first-dive-questions/reel_storyboard.json \
  --output output/first-hbot-visit-silent-draft.mp4
```

Requires local FFmpeg. Verify the slug from the supplied manifest before running.

## Shipping a RESCU.life explainer

1. Physician signs off on the script, factual references, claims, indications, contra-indications and visual depictions.
2. Designer creates original or licensed motion footage (not copied from third-party repo examples), uses the **actual authorized RESCU logo**, and honors any identifiable person consent.
3. Record and approve narration, align VTT to audio **word by word**, and obtain music usage rights.
4. Independent editor reviews the **rendered cut** for visual continuity, mobile legibility, captions, loudness and brand consistency. Fix and re-review until approved.
5. Export an accessible MP4 + WebVTT + poster. On RESCU.life, embed with native `<video controls preload="metadata" poster="...">` and `<track kind="captions" src="..." srclang="en" label="English">` once real asset URLs exist. Include a crawlable transcript and booking CTA; respect `prefers-reduced-motion` and avoid autoplay audio.
6. Confirm source truth, accessibility, links, SEO copy, performance budgets and final physician authorization. Only then separately deploy to the actual website repository/CMS.

**Critical boundary:** `Rescu1021/rescu-growth-engine` is a content and outreach engine, not RESCU.life's public frontend. This PR prepares original assets and review flows; it does **not** insert videos into RESCU.life, and it does not purport to run the restricted Anything2Explainer toolkit.

## Recommended first pilots

- TriLift: 20-second consultation/questions reel, then a longer approved explainer clarifying the components and discussing variation in outcomes.
- First HBOT visit: 20-second preparation reel and an on-site patient education explainer discussing screening and chamber differences.
- Corporate recovery/wellness: employer-focused explainer of available services, without unsupported outcomes or ROI claims.

Always keep drafts private until physician and editorial approval.
