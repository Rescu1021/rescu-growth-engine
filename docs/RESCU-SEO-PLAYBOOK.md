# RESCU.life SEO improvement worklist

**Scope:** Public Rescu.life website. This repository is the RESCU Growth Engine, **not** the website source. These changes add a read-only audit; they do not change live pages or guarantee Google indexing.

## Current live observations (8 November 2026)

- Homepage is an active, physician-owned Scarsdale entry page with a First Dive and new-client visit CTA.
- Core URLs checked: /treatments, /hbot, /trilift, /redlight-pemf, /10-pass-ozone, /skin-plan, /about, /contact and /book.
- **High priority editorial discrepancy:** /redlight-pemf displays $190 / 40 min, $50/session and $120 / 45 min in different sections. The page also juxtaposes cautious language with stronger synergy and cellular-repair claims. Review all prices, checkout links, durations, and medical claims with the practice before publishing corrections.
- Public web extractors could not confirm /robots.txt and /sitemap.xml; the GitHub Action will request them directly and report actual HTTP results. Do not infer a missing sitemap until confirmed.
- Some search results contain past/alternate appointment-menu copy: verify URL canonicals and templates, then use Search Console to investigate whether stale indexed representations need recrawling.

## Priority order (for the website repository / CMS)

1. **Trust and accuracy:** reconcile pricing, medical claims, services and current opening hours; retain physician credential and suitability disclosures. Avoid treatment/cure claims unsupported by clinical evidence.
2. **Indexability:** confirm valid HTTPS canonical per URL, accessible sitemap and robots.txt, no unintended noindex, no broken internal links, and correct permanent redirects for alternate domains and trailing slash variants.
3. **Distinct titles and descriptions:** each high-intent service page gets a descriptive unique title, Scarsdale context and an accurate meta description. Keep exactly one meaningful H1 per page.
4. **Local structured data:** valid Organization/MedicalBusiness JSON-LD on home (business name, street address, phone, official URL), and BreadcrumbList when applicable. Mark up only real, publicly visible facts; do not invent reviews, physician certifications, price ranges, or medical endorsements.
5. **Content + conversion:** human-reviewed HBOT, TriLift, Red Light + PEMF and ozone-consultation FAQs; internal links to /book; original practice photos, alt text and accessible buttons.
6. **Search measurement:** Google Search Console (index coverage, sitemap processing, top queries, impressions and CTR); Google Business Profile; optional OpenSEO project for keyword research, competitor tracking, backlinks and AI visibility.

### Suggested search-oriented page titles (review with the live CMS)

| URL | Proposed title |
| --- | --- |
| / | Physician-Led Wellness, Recovery & Aesthetics | RESCU Scarsdale |
| /hbot | Hyperbaric Oxygen Therapy in Scarsdale, NY | RESCU |
| /trilift | TriLift Facial Rejuvenation in Scarsdale, NY | RESCU |
| /redlight-pemf | Red Light + PEMF Sessions in Scarsdale, NY | RESCU |
| /10-pass-ozone | Ozone Therapy Consultations in Scarsdale, NY | RESCU |

Use real, unique meta descriptions (roughly 70–170 characters), without unsupported clinical outcomes or spammy location repetition. Prefer specific service FAQs and honest constraints to generic 'best treatment' claims.

## GitHub audit

- Run **Actions → RESCU public SEO audit → Run workflow**, or allow its weekly schedule.
- Download the **rescu-seo-report** artifact, inspect failures and resolve them in the actual website deployment repository.
- The script uses standard-library HTTP and HTML parsing, no API keys, no tracking and no access to private data.
- This lightweight audit **is not OpenSEO**: the OpenSEO open-source project is https://github.com/every-app/open-seo and its documentation is https://openseo.so/docs/chatgpt.
- Full OpenSEO metrics require connecting its plugin/MCP server and, for self-hosting, DataForSEO API credentials. Do not store those keys in GitHub files. ChatGPT must actually have OpenSEO tools available before claiming an OpenSEO scan ran.

## Draft homepage local business JSON-LD (implement in website code only after confirming business details)

\`\`\`json
{
  "@context": "https://schema.org",
  "@type": "MedicalBusiness",
  "name": "Rescu Wellness",
  "url": "https://rescu.life/",
  "telephone": "+1-914-401-8552",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "111 Brook Street, Suite 106",
    "addressLocality": "Scarsdale",
    "addressRegion": "NY",
    "postalCode": "10583",
    "addressCountry": "US"
  }
}
\`\`\`

**Do not auto-deploy** any snippet to Rescu.life without verifying the site owner/repository and reviewing clinical marketing language.
