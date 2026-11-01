# RESCU Content Factory — no paid services

Status: REVIEW-ONLY implementation. No website publication or live route changes.

The content generator uses only the Python standard library. Given editor-supplied public cited facts, it produces a mobile-readable SEO article draft, Instagram caption, four-scene 9:16 storyboard, and physician/marketing review checklist. URLs for booking include UTM parameters.

Optional video rendering uses free Pillow and FFmpeg locally. It creates a **silent MP4 proof of concept**, not a completed clinical advertisement, and does not synthesize a logo or patient outcome.

## Local commands

    python -m unittest discover -s tests
    python -m rescu_growth.content_factory --input examples/first-hbot-visit.json --output-dir output/hbot
    pip install Pillow
    python -m rescu_growth.reel_render --storyboard output/hbot/reel_storyboard.json --output output/hbot/reel.mp4

Requires Python 3.11+; FFmpeg must be installed to render videos.

## Free GitHub applications screened

- HyperFrames (Apache-2.0; github.com/heygen-com/hyperframes): local HTML-based video rendering; candidate to improve motion later.
- OpenCreator (Apache-2.0; github.com/krillinai/OpenCreator): optional local subtitle, scripting, video workspace. Some configured models/providers have costs.
- Short Video Factory (github.com/YILS-LIN/short-video-factory): optional desktop batch editor; verify commercial license and workflows.

We have NOT installed or connected any of these three vendor projects; the included local code provides the first working function without external services.

Excluded to honor free-only: ScrapeCreators paid API, Shorts Generator default paid MuAPI/LLM route, hosted AI model/API services, expensive GPU pipelines. Do not publish without explicit approval.

## Release checklist

1. Verify each linked source and clinical claim with the qualified clinical reviewer.
2. Confirm current prices, services, booking URLs and individual suitability caveats.
3. Use real authorized facility footage and RESCU's official logo; do not invent a substitute.
4. Obtain consent before using patient images, outcomes or voice; send NO patient information into research or content systems.
5. Approve titles, captions, claims, on-page canonical, sitemap routing, accessibility and tracking before publishing.
6. Measure journal entrance-to-booking conversions, not merely social views.

The existing Cloudflare Pages website and Workers routing are left unchanged.
