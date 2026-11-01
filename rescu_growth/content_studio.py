"""Batch content studio for RESCU: local drafts, image templates and review dashboard.

Python standard library for drafts; Pillow only for optional offline PNG covers.
No account access, no web requests, no publication, no paid API.
"""
from __future__ import annotations
import argparse
import csv
from html import escape
import json
from pathlib import Path

from .content_factory import build, required, tracked, https_url

COLOR = {"plum": "#481B2E", "orange": "#E7714D", "fawn": "#F9E3DB",
         "lavender": "#BAA5C0", "chalk": "#F7F7F7"}

def _font(size: int, bold: bool = False):
    from PIL import ImageFont
    names = (["/usr/share/fonts/truetype/msttcorefonts/Montserrat-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)

def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    lines, line = [], ""
    for word in text.strip().split():
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def render_cover(spec: dict, output: Path, story: bool = False) -> None:
    """Branded text artwork, not a substitute for RESCU's official logo."""
    from PIL import Image, ImageDraw
    w, h = (1080, 1920) if story else (1080, 1350)
    img = Image.new("RGB", (w, h), COLOR["plum"])
    d = ImageDraw.Draw(img)
    d.ellipse((630, 110, 1430, 920), outline=COLOR["orange"], width=6)
    d.ellipse((-390, h - 730, 550, h + 290), outline=COLOR["lavender"], width=5)
    d.rounded_rectangle((66, 74, 245, 86), radius=6, fill=COLOR["orange"])
    d.text((66, 125), "RESCU WELLNESS", font=_font(38, True), fill=COLOR["fawn"])
    d.text((66, 188), "SCARSDALE  /  PHYSICIAN-LED", font=_font(26), fill=COLOR["lavender"])
    heading = spec["hook"]
    size = 94
    while True:
        face = _font(size, True)
        lines = _wrap(d, heading, face, w - 145)
        line_height = int(size * 1.28)
        if len(lines) * line_height < int(h * .45) or size <= 42:
            break
        size -= 4
    y = int(h * .28) if story else int(h * .30)
    for line in lines:
        d.text((67, y), line, font=face, fill=COLOR["chalk"])
        y += line_height
    d.text((68, h - 294), spec["service"].upper()[:44], font=_font(29, True), fill=COLOR["orange"])
    d.rounded_rectangle((65, h - 220, w - 65, h - 125), radius=25, fill=COLOR["orange"])
    cta = _wrap(d, spec["cta_label"], _font(34, True), w - 186)
    for i, line in enumerate(cta[:2]):
        d.text((90, h - 206 + i * 37), line, font=_font(34, True), fill=COLOR["plum"])
    d.text((68, h - 85), "DRAFT / MEDICAL REVIEW REQUIRED", font=_font(22), fill=COLOR["fawn"])
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, format="PNG", optimize=True)

def _index(rows: list[dict]) -> str:
    cards = []
    for r in rows:
        slug = escape(r["slug"], quote=True)
        title = escape(r["title"])
        hook = escape(r["hook"])
        cards.append(f'''<article class="card">
<img src="campaigns/{slug}/cover-post.png" alt="Draft cover for {title}" loading="lazy">
<div class="body"><div class="tag">REVIEW REQUIRED · {escape(r["service"])}</div>
<h2>{title}</h2><p>{hook}</p>
<div class="links"><a href="campaigns/{slug}/landing.html">Article</a>
<a href="campaigns/{slug}/instagram.txt">Caption</a>
<a href="campaigns/{slug}/reel_storyboard.json">Storyboard</a>
<a href="campaigns/{slug}/review.json">Review</a>
<a href="campaigns/{slug}/cover-story.png">Story</a></div>
</div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RESCU Content Factory | Internal Drafts</title>
<style>
:root{{--p:#481B2E;--o:#E7714D;--f:#F9E3DB;--l:#BAA5C0}}
*{{box-sizing:border-box}}body{{margin:0;background:#faf7f8;font:16px/1.5 Arial,sans-serif;color:var(--p)}}
header{{background:var(--p);color:white;padding:48px max(20px,calc((100vw - 1220px)/2));}}
header p{{max-width:750px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05;margin:18px 0}}
.kicker{{color:var(--l);font-weight:700;letter-spacing:.12em}}
.notice{{background:var(--f);padding:14px;border-left:5px solid var(--o);margin:24px auto;max-width:1220px}}
main{{max-width:1220px;margin:auto;padding:6px 20px 60px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:24px}}
.card{{background:white;border-radius:20px;overflow:hidden;box-shadow:0 10px 30px #481b2e16}}
.card img{{width:100%;height:250px;object-fit:cover;object-position:50% 36%}}
.body{{padding:22px}}.tag{{color:#9b482e;font-size:12px;font-weight:700;letter-spacing:.05em}}
h2{{line-height:1.2;font-size:21px}}.links{{display:flex;gap:12px;flex-wrap:wrap}}
a{{color:#782b44}}a:focus-visible{{outline:3px solid var(--o);outline-offset:3px}}
footer{{padding:25px;text-align:center;border-top:1px solid #eadfe5}}
</style></head><body>
<header><div class="kicker">RESCU · CONTENT STUDIO</div>
<h1>Campaigns, ready for review.</h1>
<p>{len(rows)} campaign packs generated locally. Includes articles, captions, storyboards, post images, story images and tracked URLs.</p></header>
<div class="notice"><strong>PRIVATE DRAFTS.</strong> None of these assets are approved medical advertising, live on Rescu.life, or scheduled for publication.</div>
<main><p><a href="content-calendar.csv">Editorial calendar</a> ·
<a href="campaign-links.csv">Tracked links</a> ·
<a href="measurement-template.csv">Measurement template</a></p>
<div class="grid">{''.join(cards)}</div></main>
<footer>No patient data · No paid API · Human review before publishing</footer></body></html>'''

def produce(manifest: dict, output_root: Path, *, pngs: bool = True) -> dict:
    specs = manifest.get("campaigns")
    if not isinstance(specs, list) or not (1 <= len(specs) <= 20):
        raise ValueError("manifest needs between 1 and 20 campaign objects")
    seen: set[str] = set()
    validated = []
    # Validate the entire batch before writing anything.
    for spec in specs:
        pack = build(spec)
        slug = spec["slug"]
        if slug in seen:
            raise ValueError("Duplicate campaign slug: " + slug)
        seen.add(slug)
        validated.append((spec, pack))
    output_root.mkdir(parents=True, exist_ok=True)
    rows = []
    link_rows = []
    for i, (spec, pack) in enumerate(validated, 1):
        slug = spec["slug"]
        folder = output_root / "campaigns" / slug
        folder.mkdir(parents=True, exist_ok=True)
        for name, content in pack.items():
            (folder / name).write_text(content + "\n", encoding="utf-8")
        if pngs:
            render_cover(spec, folder / "cover-post.png")
            render_cover(spec, folder / "cover-story.png", story=True)
        rows.append({"slot": f"Week {1 + (i-1)//2}, post {1 + (i-1)%2}",
                     "slug": slug, "service": spec["service"],
                     "title": spec["title"], "hook": spec["hook"],
                     "channel": "Instagram + Journal + 9:16 Reel",
                     "status": "DRAFT_REQUIRES_REVIEW"})
        link_rows.append({"slug": slug,
             **{m: tracked(https_url(spec["cta_url"], cta=True), slug, m)
                for m in ("article", "instagram", "reel")}})
    def save_csv(name, records):
        with (output_root / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    save_csv("content-calendar.csv", rows)
    save_csv("campaign-links.csv", link_rows)
    save_csv("measurement-template.csv",
             [{"slug": r["slug"], "week": r["slot"], "entrances": "",
               "cta_clicks": "", "consult_bookings": "", "package_sales": "",
               "notes": ""} for r in rows])
    if pngs:
        (output_root / "index.html").write_text(_index(rows), encoding="utf-8")
    (output_root / "MANUAL-REVIEW.txt").write_text(
        "RESCU Content Factory — internal campaign review\n"
        "Each generated claim requires source and physician verification.\n"
        "None of these files were published, posted, mailed, or sent to leads.\n"
        "For source URLs pointing at RESCU, verify that they actually support the fact.\n"
        "Use the official RESCU logo only when an approved asset is supplied.\n",
        encoding="utf-8")
    return {"campaigns": len(rows), "png_generated": pngs,
            "output_dir": str(output_root)}

def main():
    parser = argparse.ArgumentParser(description="Build RESCU's local review-only content studio")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--no-images", action="store_true")
    parser.add_argument("--logo-path", type=Path, help="Official RESCU logo image downloaded with permission")
    parser.add_argument("--photo-sheet", type=Path, help="Licensed/AI-generated 4x2 photo sheet for editorial design")
    args = parser.parse_args()
    summary = produce(json.loads(args.manifest.read_text(encoding="utf-8")),
                      args.output_dir, pngs=not args.no_images)
    if args.logo_path or args.photo_sheet:
        if args.no_images or not args.logo_path or not args.photo_sheet:
            parser.error("Provide both --logo-path and --photo-sheet, without --no-images")
        from .editorial_design import render as render_editorial
        render_editorial(args.manifest, args.logo_path, args.photo_sheet, args.output_dir)
        summary["design"] = "Pinterest-inspired editorial with official RESCU logo"
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
