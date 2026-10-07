# Rescu Growth CRM Worker

Dedicated Cloudflare Worker for the Rescu Growth Engine ↔ Twenty CRM integration.

This is intentionally separate from the production Rescu Concierge Worker.

## Cloudflare project

`rescu-growth-crm`

## Required runtime configuration

Set these in Cloudflare, not GitHub:

- `TWENTY_API_KEY` — encrypted secret
- `TWENTY_BASE_URL` — `https://resculife.twenty.com`

Never commit the Twenty API key.

## Deploy from GitHub

Create a Cloudflare Worker connected to this repository and set the root directory to `worker`.
Build command: `npm install`
Deploy command: `npx wrangler deploy`

After the secret and base URL are configured, the next phase adds Twenty CRM objects, pipeline synchronization, owner routing, response state, recycle/reactivation, and revenue attribution.
