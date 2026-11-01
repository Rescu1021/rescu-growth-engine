# PR preview build

The November 1, 2026 build of commit `65f7872` failed during Cloudflare's
automatic `pip install .`, before Wrangler ran. Setuptools discovered multiple
top-level packages (`data`, `config`, `worker`, `rescu_growth`). The package list
in `pyproject.toml` now explicitly includes only `rescu_growth`. CI installs the
package and imports it outside the checkout before running the offline tests.

## Cloudflare preview trigger

The existing trigger is restricted to `feature/rescu-content-factory-20261031`.
Keep the repository root `/` and the empty build command. Its preview command is:

```sh
npx --yes wrangler@4.156.0 preview --config worker/wrangler.jsonc --worker-name rescu-growth-engine --ignore-base-config
```

The explicit config path fixes discovery from the repository root. The explicit
Worker target matches the existing Cloudflare project, while preserving the
`rescu-growth-crm` name in the original Worker config. The empty `previews` block
and `--ignore-base-config` keep this preview free of CRM credentials and bindings.
This command creates a branch Preview; it does not promote a production version.
Do not replace it with `wrangler deploy` or change production branch settings.

## Verification

```sh
python -m pip install . Pillow
python -I -c "from rescu_growth import content_studio, editorial_design"
python -m unittest discover -s tests -v
python -m rescu_growth.content_studio --manifest examples/2026-rescu-eight-campaigns.json --output-dir /tmp/rescu-drafts
npx --yes wrangler@4.156.0 deploy --dry-run --config worker/wrangler.jsonc --outdir /tmp/rescu-worker
```

The dry run bundles locally without uploading. After a successful Cloudflare
preview build, use its returned Preview URL: `/health` should report `ok: true`
and all three configuration flags false; `/routing/preview?service=HBOT` should
report `writesPerformed: 0`; `/admin/health` should fail closed with HTTP 503.
Compare the active production deployment ID before and after verification.

The Cloudflare URL previews the existing CRM Worker. Content Factory generates
the separate offline HTML dashboard and campaign files. The official Drive logo
and photo sheet remain external inputs, as documented in `EDITORIAL-REDESIGN.md`;
this fix does not publish those assets or the generated campaign drafts.
