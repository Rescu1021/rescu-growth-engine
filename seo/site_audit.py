#!/usr/bin/env python3
"""Read-only technical SEO audit of public RESCU pages, using the Python standard library.

No patient information, credentials, analytics cookies, or paid SEO APIs are used.
Findings are signals for manual review, not claims about Google's indexing decisions.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SITE = "https://rescu.life"
PATHS = (
    "/", "/treatments", "/hbot", "/trilift", "/redlight-pemf",
    "/10-pass-ozone", "/skin-plan", "/about", "/contact",
    "/book", "/black-friday/",
)
USER_AGENT = "RESCU-SEO-Audit/1.0 (public site health checks)"


@dataclass
class Page:
    url: str
    status: int = 0
    title: str = ""
    description: str = ""
    canonical: str = ""
    robots: str = ""
    h1s: list[str] = field(default_factory=list)
    schemas: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


class SEOParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.h1_parts: list[list[str]] = []
        self.schema_blocks: list[str] = []
        self._in_title = False
        self._in_h1 = False
        self._in_jsonld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {key.lower(): (value or "") for key, value in attrs}
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True
            self.h1_parts.append([])
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self.schema_blocks.append("")
        elif tag == "meta":
            key = a.get("name", "").lower()
            if key == "description":
                self.description = a.get("content", "")
            elif key == "robots":
                self.robots = a.get("content", "")
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = a.get("href", "")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_h1 and self.h1_parts:
            self.h1_parts[-1].append(data)
        if self._in_jsonld and self.schema_blocks:
            self.schema_blocks[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "script":
            self._in_jsonld = False

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1s(self) -> list[str]:
        return [" ".join("".join(parts).split()) for parts in self.h1_parts]

    @property
    def schemas(self) -> list[str]:
        found: list[str] = []

        def extract(obj: object) -> None:
            if isinstance(obj, list):
                for item in obj:
                    extract(item)
            elif isinstance(obj, dict):
                value = obj.get("@type")
                if isinstance(value, str):
                    found.append(value)
                elif isinstance(value, list):
                    found.extend(str(v) for v in value)
                if "@graph" in obj:
                    extract(obj["@graph"])

        for block in self.schema_blocks:
            try:
                extract(json.loads(block))
            except (ValueError, TypeError):
                continue
        return found


def normalized(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    return f"{parts.scheme.lower()}://{parts.netloc.lower()}{path}"


def inspect_html(url: str, html: str, status: int = 200) -> Page:
    p = SEOParser()
    p.feed(html)
    page = Page(
        url=url, status=status, title=p.title, description=p.description.strip(),
        canonical=urljoin(url, p.canonical) if p.canonical else "",
        robots=p.robots, h1s=p.h1s, schemas=p.schemas,
    )
    if status >= 400:
        page.issues.append(f"HTTP {status}")
        return page
    if not page.title:
        page.issues.append("Missing title")
    elif len(page.title) > 65:
        page.issues.append("Title longer than 65 characters")
    if not page.description:
        page.issues.append("Missing meta description")
    elif not 70 <= len(page.description) <= 170:
        page.issues.append("Review meta description length")
    if len(page.h1s) != 1:
        page.issues.append(f"Expected one H1; found {len(page.h1s)}")
    if not page.canonical:
        page.issues.append("Missing rel=canonical")
    elif normalized(page.canonical) != normalized(url):
        page.issues.append(f"Canonical points elsewhere: {page.canonical}")
    if re.search(r"\bnoindex\b", page.robots, re.IGNORECASE):
        page.issues.append("Meta robots contains noindex; confirm intentional")
    if urlsplit(url).path in ("", "/", "/contact"):
        if "10583" not in html or "914-401-8552" not in html:
            page.issues.append("Check visible local address and phone (NAP)")
    if urlsplit(url).path in ("", "/") and not any(
        s in page.schemas for s in ("LocalBusiness", "MedicalBusiness", "MedicalClinic", "Organization")
    ):
        page.issues.append("Review homepage organization/local business JSON-LD")
    return page


def read_url(url: str) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/plain"})
    try:
        with urlopen(req, timeout=15) as response:
            raw = response.read(3_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return response.status, raw.decode(charset, errors="replace")
    except HTTPError as exc:
        return exc.code, ""
    except (URLError, TimeoutError, OSError) as exc:
        return 0, str(exc)


def check_site_files(base: str) -> list[str]:
    notes: list[str] = []
    for path in ("/robots.txt", "/sitemap.xml"):
        status, body = read_url(base + path)
        if status != 200:
            notes.append(f"{path}: HTTP {status or 'network error'} (verify directly; a bot challenge is possible)")
        elif path == "/sitemap.xml":
            try:
                root = ET.fromstring(body)
                urls = root.findall(".//{*}loc")
                notes.append(f"{path}: accessible; {len(urls)} URL/sitemap entries")
            except ET.ParseError:
                notes.append(f"{path}: HTTP 200 but XML could not be parsed")
        elif "Sitemap:" not in body:
            notes.append(f"{path}: accessible; consider an explicit Sitemap: directive")
        else:
            notes.append(f"{path}: accessible with a Sitemap: directive")
    return notes


def audit(base: str = SITE, paths: tuple[str, ...] = PATHS) -> tuple[list[Page], list[str]]:
    base = base.rstrip("/")
    pages: list[Page] = []
    for path in paths:
        url = base + path
        status, body = read_url(url)
        if status == 200:
            pages.append(inspect_html(url, body, status))
        else:
            page = Page(url=url, status=status)
            page.issues.append(f"HTTP {status or 'network error'}")
            pages.append(page)
    by_title: dict[str, list[Page]] = {}
    for page in pages:
        if page.title:
            by_title.setdefault(page.title.casefold(), []).append(page)
    for group in by_title.values():
        if len(group) > 1:
            for page in group:
                page.issues.append("Duplicate title across checked URLs")
    return pages, check_site_files(base)


def render(pages: list[Page], site_notes: list[str]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# RESCU technical SEO check", "",
        f"Generated: {now}", "",
        "Read-only check of selected public pages. Warnings require review; this is not Search Console or Google index-status data.",
        "",
        "| Page | HTTP | Title | Description | H1 count | Findings |",
        "| --- | ---: | --- | --- | ---: | --- |",
    ]
    for p in pages:
        path = urlsplit(p.url).path or "/"
        label = p.title.replace("|", "/")[:65] or "—"
        desc = f"{len(p.description)} chars" if p.description else "—"
        findings = "; ".join(p.issues).replace("|", "/") or "No basic on-page issues flagged"
        lines.append(f"| {path} | {p.status or 'ERR'} | {label} | {desc} | {len(p.h1s)} | {findings} |")
    lines.extend(["", "## Crawl endpoints", ""])
    lines.extend(f"- {note}" for note in site_notes)
    lines.extend([
        "", "## Manual editorial review (not automated medical verification)", "",
        "- Reconcile Red Light + PEMF prices and appointment durations across the page and checkout links.",
        "- Review any medical-effect claims and remove unsupported promises of treatment efficacy or synergy.",
        "- Verify business hours, contact details and physician credentials across service and location pages.",
        "- Use Search Console to confirm actual indexing, coverage and query impressions.",
        "- Use OpenSEO / DataForSEO separately for rankings, competitor terms, backlinks and AI visibility.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Public RESCU SEO audit; does not modify the website.")
    parser.add_argument("--site", default=SITE, help="Site origin, default https://rescu.life")
    parser.add_argument("--output", default="seo-report.md", help="Markdown report path")
    args = parser.parse_args()
    base = args.site.rstrip("/")
    if urlsplit(base).scheme != "https":
        parser.error("--site must be an HTTPS origin")
    pages, notes = audit(base)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(pages, notes), encoding="utf-8")
    print(f"Wrote {output}: {len(pages)} pages, {sum(bool(p.issues) for p in pages)} with review flags.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
