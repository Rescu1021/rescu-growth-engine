"""Free, local, review-first RESCU content pack builder. No paid APIs or PHI."""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

COLORS = {"plum": "#481B2E", "tangerine": "#E7714D", "fawn": "#F9E3DB"}
SENSITIVE_FIELDS = {"patient", "patient_name", "patient_email", "patient_phone", "dob", "date_of_birth", "diagnosis", "medical_record"}
RISKY = (r"\bcures?\b", r"\bguarantee[ds]?\b", r"\b100%\b", r"\bno downtime\b", r"\bfda.approved\b", r"\bproven to treat\b", r"\binstant results\b")

def required(data: dict, field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required text: {field}")
    return value.strip()

def https_url(url: str, *, cta: bool = False) -> str:
    p = urlsplit(url.strip())
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("Only HTTPS URLs without credentials are permitted")
    if cta and p.hostname.lower() not in {"rescu.life", "www.rescu.life"}:
        raise ValueError("CTA URL must point to rescu.life")
    return url.strip()

def tracked(url: str, slug: str, medium: str) -> str:
    p = urlsplit(url)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    q.update(utm_source="rescu_content_factory", utm_medium=medium, utm_campaign=slug)
    return urlunsplit(p._replace(query=urlencode(q)))

def build(spec: dict) -> dict:
    if not isinstance(spec, dict):
        raise ValueError("Input must be a JSON object")
    blocked = set(spec).intersection(SENSITIVE_FIELDS)
    if blocked:
        raise ValueError("Patient fields are prohibited: " + ", ".join(sorted(blocked)))
    slug = required(spec, "slug")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,69}", slug):
        raise ValueError("slug must be lowercase letters, digits, hyphens, 3-70 characters")
    title = required(spec, "title")
    intro = required(spec, "intro")
    hook = required(spec, "hook")
    service = required(spec, "service")
    cta_label = required(spec, "cta_label")
    cta_url = https_url(required(spec, "cta_url"), cta=True)
    facts = spec.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ValueError("At least one cited fact is required")
    vetted = []
    for index, item in enumerate(facts, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Fact {index} is not an object")
        vetted.append({"text": required(item, "text"), "source_url": https_url(required(item, "source_url"))})
    text = " ".join([title, intro, hook, cta_label] + [f["text"] for f in vetted])
    flags = [regex for regex in RISKY if re.search(regex, text, re.I)]
    html_facts = "\n".join(
        f'<li>{escape(f["text"])} <a href="{escape(f["source_url"], quote=True)}" rel="noopener noreferrer">Source {i}</a></li>'
        for i, f in enumerate(vetted, 1)
    )
    canonical = f"https://rescu.life/journal/{slug}"
    booking = tracked(cta_url, slug, "article")
    caption_booking = tracked(cta_url, slug, "instagram")
    html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(intro[:155], quote=True)}">
<link rel="canonical" href="{escape(canonical, quote=True)}">
<style>:root{{--plum:{COLORS['plum']};--orange:{COLORS['tangerine']};--fawn:{COLORS['fawn']}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--fawn);font-family:Montserrat,Arial,sans-serif;color:var(--plum);line-height:1.65}}
main{{max-width:850px;margin:0 auto;padding:4rem 1.25rem 6rem}}.eyebrow{{font-size:.85rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800;color:#8d432c}}
h1{{font-size:clamp(2.1rem,6vw,3.8rem);line-height:1.12}}.lead{{font-size:1.25rem}}section{{background:white;padding:1.5rem 2rem;border-radius:18px;margin-top:2rem}}
li{{margin:1rem 0}}a{{color:#8e371d}}a:focus-visible{{outline:3px solid var(--orange);outline-offset:4px}}
.cta{{display:inline-block;border-radius:12px;background:var(--plum);color:#fff;text-decoration:none;padding:1rem 1.5rem;font-weight:800;min-height:44px}}
footer{{font-size:.85rem;margin-top:2rem}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}</style></head>
<body><main><p class="eyebrow">RESCU Wellness · {escape(service)} · Scarsdale, NY</p><h1>{escape(title)}</h1>
<p class="lead">{escape(intro)}</p><section aria-labelledby="points"><h2 id="points">What to know</h2><ul>{html_facts}</ul></section>
<section aria-labelledby="next"><h2 id="next">Explore your options</h2><p>Discuss suitability, current offers and scheduling with the clinical team.</p>
<p><a class="cta" href="{escape(booking, quote=True)}">{escape(cta_label)}</a></p></section>
<footer>Educational information only. Not a diagnosis or a promise of outcomes. This is an unpublished draft requiring clinical approval.</footer>
</main></body></html>'''
    caption = "\n\n".join([hook, intro, "\n".join("• " + f["text"] for f in vetted[:3]),
                             f"{cta_label}: {caption_booking}",
                             "Educational information only. Clinical assessment determines suitability."])
    storyboard = {
        "format": "9:16", "service": service, "requires_clinical_approval": True,
        "slides": [
            {"seconds": [0, 4], "title": hook, "visual": "Approved clinic video or plum background"},
            {"seconds": [4, 10], "title": intro, "visual": "Approved facility detail or safe animation"},
            {"seconds": [10, 16], "title": vetted[0]["text"], "visual": "On-screen text and source link in production notes"},
            {"seconds": [16, 20], "title": cta_label, "visual": "CTA with approved logo if supplied"},
        ],
        "booking": tracked(cta_url, slug, "reel"),
        "creative_rules": ["Use real approved RESCU logo, never a substitute",
                           "No invented patient outcomes", "Caption all dialogue", "Preserve source citations"],
    }
    review = {"status": "NOT APPROVED — NO AUTO-PUBLISH", "slug": slug, "title": title,
              "sources": [f["source_url"] for f in vetted], "risky_claim_flags": flags,
              "checklist": ["Physician verifies every medical claim and citation",
                            "Confirm current pricing, service eligibility and booking URLs",
                            "Check image and voice consent; no PHI or patient examples",
                            "Verify brand assets and trademark use",
                            "Check mobile layout, accessibility and canonical before deploy",
                            "A human approves and publishes each asset"]}
    return {"landing.html": html_doc, "instagram.txt": caption,
            "reel_storyboard.json": json.dumps(storyboard, indent=2),
            "review.json": json.dumps(review, indent=2)}

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate free RESCU content drafts; never publishes")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    pack = build(json.loads(args.input.read_text(encoding="utf-8")))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, contents in pack.items():
        (args.output_dir / name).write_text(contents + "\n", encoding="utf-8")
    print("Wrote unapproved content drafts to", args.output_dir)

if __name__ == "__main__":
    main()
