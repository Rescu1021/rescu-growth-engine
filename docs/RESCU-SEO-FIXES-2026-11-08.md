# Rescu.life implementation checklist — OpenSEO audit, 2026-11-08

**Status: Prepared, NOT deployed.** The Cloudflare connection currently returns HTTP 403 for Pages projects (`page.read/page.write` scope missing), Workers scripts (read/edit missing), and zone inspection (`zone.read` missing). None of the three GitHub repositories visible to the connected account contains the live Rescu.life page source. Do not substitute this repo for the production website.

OpenSEO project: https://app.openseo.so/p/eaf97721-ec15-4f77-a0d9-561d3a771b95
Audit: https://app.openseo.so/p/eaf97721-ec15-4f77-a0d9-561d3a771b95/audit?auditId=724efd57-da62-485d-a6be-341563712438
Report: https://app.openseo.so/p/eaf97721-ec15-4f77-a0d9-561d3a771b95/reports/cf092526-0372-4a8e-a6dd-5351cd6e772c

## Completed crawl findings

- 50 of 50 crawled pages returned HTTP 200 and the crawler marked them indexable and sitemap-included.
- 0 critical issue instances.
- 6 **warning** instances: multiple H1s.
- 42 **informational** instances: heading levels skipped.
- 2 **informational** instances: meta descriptions over 160 characters.
- Google indexing not verified: Search Console not linked in OpenSEO; GA4 not linked either.

## Must fix in ACTUAL production source

### Duplicate H1s — six URL paths
- /facials-laser
- /geneo
- /shockwave
- /styku-proteus
- /t6000
- /vanquishme

Keep the semantic primary page heading as the sole H1 and demote secondary headings only after checking page meaning and CSS. Don't remove headings just to satisfy the validator. Prefer correcting the shared template if responsible.

### Heading hierarchy — 42 page paths
- /10-pass-ozone
- /about
- /beauty-aesthetics-scarsdale
- /bronxville-wellness
- /bundles
- /champions
- /contact
- /emsculpt-neo
- /emsella
- /equinox-scarsdale-recovery-spa-alternative
- /executive-wellness-longevity-westchester
- /facials-laser
- /geneo
- /glp1-peptides
- /greenwich-ct-wellness
- /hbot
- /larchmont-wellness
- /laser-hair-removal
- /life-time-westchester-recovery-longevity-alternative
- /lightstim
- /new-rochelle-wellness
- /nyc-wellness
- /pain-injury-recovery-westchester
- /pemf
- /pickleball-recovery-westchester
- /redlight-pemf
- /red-light-therapy-westchester
- /restore-hyper-wellness-eastchester-scarsdale-alternative
- /rf-microneedling
- /shockwave
- /stellar-m22
- /styku-proteus
- /t6000
- /tarrytown-wellness
- /transform-fitness-recovery-performance-alternative
- /trilift
- /trilift-case-study
- /trilift-westchester
- /vanquishme
- /westchester-recovery-longevity-wellness-alternatives
- /where-to-start
- /yonkers-wellness

Keep a logical nested outline (H1 > H2 > H3) without jumps. Use CSS classes to preserve visual styles rather than styling solely by heading element.

### Meta descriptions — two URL paths
**/hbot** (current: 164 characters):
```html
<meta name="description" content="Explore physician-screened hyperbaric oxygen therapy at RESCU Wellness in Scarsdale, NY. Compare chamber options and ask about the $199 first dive.">
```

**/10-pass-ozone** (current: 207 characters):
```html
<meta name="description" content="Learn about physician-screened 10-Pass ozone consultations at RESCU Wellness in Scarsdale, NY. Review evidence, risks and appointment options.">
```

Only apply these in the single source of truth for each page; preserve working canonicals and Open Graph data. Clinical claims should be physician-reviewed; these proposed descriptions are not medical-efficacy promises.

## Important editorial and operational review (outside crawler scope)

1. /redlight-pemf: Compare all displayed $190, $120, and $50 prices, session duration and checkout terms against the approved current price list. Remove inconsistent or expired offers **only after** the practice's current prices are confirmed. Avoid automatically replacing with an unverified number.
2. /about and /contact: Verify onsite physician schedule and business operating hours and make both pages consistent.
3. /glp1-peptides: Verify current prescribing/compliance and the exact program prices against approved operations; do not silently imply availability of regulated products.
4. All medical services: Have a clinician review effectiveness/synergy/disease-treatment claims, especially ozone and Red Light + PEMF. The SEO crawler does not validate clinical evidence.
5. Local suburb landing pages: Ensure each offers unique service-relevant value and correctly states the actual Scarsdale address (not a fictional branch).
6. Verify checkout and WhatsApp conversion links after any page-content edits.

## Deployment safeguards / acceptance tests

1. Locate the authentic Pages/Workers project and its Git origin. Create a branch/preview instead of editing production at the edge.
2. Change shared heading components then the exceptional pages. Compare rendered mobile/desktop pages and booking routes.
3. Validate 50 pages as HTTP 200, titles/meta present and unique, all canonical URLs correctly scoped, one H1 per page, zero skipped heading levels, all links working and zero new noindex directives.
4. Make sure sitemap and robots.txt stay accessible. Google indexability must subsequently be checked in Search Console, not inferred from crawler flags.
5. Run a new OpenSEO audit on the preview or after the reviewed deployment, and compare to audit `724efd57-da62-485d-a6be-341563712438`.

## Blocker to production edits

Cloudflare reconnect must grant Pages Read and Pages Write (if this is a Pages project), Workers Scripts Read and Editor (if this is Workers), and Zone Read to identify routing, or grant access to the separate actual production Git repository. No deployment has occurred.
