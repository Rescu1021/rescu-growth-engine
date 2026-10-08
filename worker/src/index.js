import { routeLead } from "./rescu-routing.js";
const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });

const baseUrl = (env) => (env.TWENTY_BASE_URL || "").replace(/\/$/, "");

async function twentyFetch(env, path, init = {}) {
  if (!env.TWENTY_API_KEY || !baseUrl(env)) throw new Error("twenty_not_configured");
  const headers = new Headers(init.headers || {});
  headers.set("Authorization", `Bearer ${env.TWENTY_API_KEY}`);
  headers.set("Content-Type", "application/json");
  const response = await fetch(`${baseUrl(env)}${path}`, { ...init, headers });
  const text = await response.text();
  let body;
  try { body = text ? JSON.parse(text) : null; } catch { body = { raw: text }; }
  if (!response.ok) {
    const error = new Error("twenty_api_error");
    error.status = response.status;
    error.body = body;
    throw error;
  }
  return body;
}

async function probeTwenty(env) {
  const candidates = ["/rest/people?limit=1", "/rest/companies?limit=1"];
  let lastError;
  for (const path of candidates) {
    try {
      await twentyFetch(env, path);
      return { connected: true, endpoint: path };
    } catch (error) {
      lastError = error;
      if (error.status === 401 || error.status === 403) break;
    }
  }
  return {
    connected: false,
    status: lastError?.status || 500,
    detail: lastError?.body || lastError?.message || "unknown_error",
  };
}

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function isAdmin(request, env) {
  if (!env.RESCU_ADMIN_TOKEN) return false;
  const auth = request.headers.get("authorization") || "";
  const supplied = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  return timingSafeEqual(supplied, env.RESCU_ADMIN_TOKEN);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/health")) {
      return json({
        ok: true,
        service: "rescu-growth-crm",
        twentyConfigured: Boolean(env.TWENTY_API_KEY),
        twentyBaseUrlConfigured: Boolean(env.TWENTY_BASE_URL),
        adminProtectionConfigured: Boolean(env.RESCU_ADMIN_TOKEN),
      });
    }

    if (request.method === "GET" && url.pathname === "/health/twenty") {
      if (!env.TWENTY_API_KEY || !env.TWENTY_BASE_URL) {
        return json({ ok: false, connected: false, error: "twenty_not_configured" }, 503);
      }
      const result = await probeTwenty(env);
      return json({ ok: result.connected, ...result }, result.connected ? 200 : 502);
    }

    // Read-only metadata discovery. Returns only object IDs/names, never CRM records.
    // This lets us verify the live Twenty metadata API shape before enabling any
    // provisioning mutation.
    if (request.method === "GET" && url.pathname === "/health/twenty/metadata") {
      if (!env.TWENTY_API_KEY || !env.TWENTY_BASE_URL) {
        return json({ ok: false, error: "twenty_not_configured" }, 503);
      }
      try {
        const body = await twentyFetch(env, "/rest/metadata/objects");
        const raw = Array.isArray(body) ? body : (body?.data || body?.objects || []);
        const objects = Array.isArray(raw)
          ? raw.map((o) => ({
              id: o?.id || null,
              nameSingular: o?.nameSingular || null,
              namePlural: o?.namePlural || null,
              labelSingular: o?.labelSingular || null,
            })).filter((o) => o.id || o.nameSingular || o.namePlural)
          : [];
        return json({ ok: true, count: objects.length, objects });
      } catch (error) {
        return json({
          ok: false,
          error: "metadata_probe_failed",
          status: error?.status || 500,
          detail: error?.body || error?.message || "unknown_error",
        }, 502);
      }
    }

    // Public deterministic routing preview; does not query or write CRM records.
    if (request.method === "GET" && url.pathname === "/routing/preview") {
      const campaign = (url.searchParams.get("campaign") || "").slice(0, 120);
      const service = (url.searchParams.get("service") || "").slice(0, 120);
      return json({ ok: true, mode: "preview", writesPerformed: 0,
        campaign, service, ...routeLead({ campaign, service }) });
    }

    // All future CRM mutation/provisioning routes live under /admin/*.
    // They fail closed unless a runtime RESCU_ADMIN_TOKEN secret exists and
    // the caller supplies the same value as Authorization: Bearer <token>.
    if (url.pathname.startsWith("/admin/")) {
      if (!env.RESCU_ADMIN_TOKEN) {
        return json({ ok: false, error: "admin_protection_not_configured" }, 503);
      }
      if (!isAdmin(request, env)) {
        return json({ ok: false, error: "unauthorized" }, 401);
      }

      // Authenticated intake validation only. No record writes until the
      // deduplication and CRM create workflow is verified separately.
      if (request.method === "POST" && url.pathname === "/admin/intake/preview") {
        let data;
        try { data = await request.json(); } catch {
          return json({ ok: false, error: "invalid_json" }, 400);
        }
        const campaign = typeof data?.campaign === "string" ? data.campaign.slice(0, 120) : "";
        const service = typeof data?.service === "string" ? data.service.slice(0, 120) : "";
        const source = typeof data?.source === "string" ? data.source.slice(0, 120) : "";
        const externalId = typeof data?.externalId === "string" ? data.externalId.slice(0, 120) : "";
        if (!campaign && !service) return json({ ok: false, error: "campaign_or_service_required" }, 400);
        if (!source || !externalId || !/^[a-zA-Z0-9_-]{8,120}$/.test(externalId)) {
          return json({ ok: false, error: "valid_source_and_opaque_external_id_required" }, 400);
        }
        const route = routeLead({ campaign, service });
        // Paginated read-only duplicate scan. Never treat a full or ambiguous
        // response as evidence that a lead is new.
        let duplicateCheck = "not_checked";
        try {
          let scanned = 0;
          let found = false;
          let complete = false;
          for (let offset = 0; offset < 1000; offset += 100) {
            const result = await twentyFetch(env, "/rest/opportunities?limit=100&offset=" + offset);
            const rows = Array.isArray(result?.data?.opportunities) ? result.data.opportunities :
              Array.isArray(result?.opportunities) ? result.opportunities : null;
            if (!rows) return json({ ok: false, error: "dedup_response_unrecognized" }, 502);
            if (offset > 0 && rows.length && result?.pagination === undefined &&
                result?.pageInfo === undefined && result?.meta === undefined) {
              // Offset behavior cannot be verified; do not claim completeness.
              duplicateCheck = "inconclusive_pagination_unverified";
              break;
            }
            scanned += rows.length;
            if (rows.some(row => row.rescuExternalId === externalId && row.rescuSource === source)) {
              found = true;
              break;
            }
            if (rows.length < 100) { complete = true; break; }
          }
          if (found) duplicateCheck = "duplicate_found";
          else if (complete) duplicateCheck = "not_found_in_current_records";
          else if (duplicateCheck === "not_checked") duplicateCheck = "inconclusive_limit_reached";
        } catch {
          return json({ ok: false, error: "dedup_lookup_failed" }, 502);
        }
        return json({
          ok: true, mode: "dry_run", writesPerformed: 0,
          duplicateCheck,
          proposedOpportunity: {
            stage: "DISCOVERED", campaign, source, externalId,
            routingOwner: route.routingOwner,
            automationState: route.automationState,
            suppressed: true
          },
          nextStep: "verify_deduplication_before_enabling_writes"
        });
      }

      // Explicitly gated automatic intake. No public form or outbound messaging.
      // All callers must use the admin bearer secret.
      if (request.method === "POST" && url.pathname === "/admin/intake/create") {
        if (env.RESCU_AUTO_INTAKE_ENABLED !== "true") {
          return json({ ok: false, error: "auto_intake_not_enabled" }, 503);
        }
        let data;
        try { data = await request.json(); } catch {
          return json({ ok: false, error: "invalid_json" }, 400);
        }
        const allowed = ["source", "externalId", "campaign", "service"];
        if (!data || typeof data !== "object" || Array.isArray(data) ||
            Object.keys(data).some(k => !allowed.includes(k)) ||
            Object.values(data).some(v => typeof v !== "string" || v.length > 120)) {
          return json({ ok: false, error: "invalid_payload" }, 400);
        }
        const { source, externalId, campaign = "", service = "" } = data;
        if (!source || !/^[a-zA-Z0-9_-]{8,120}$/.test(externalId || "") ||
            (!campaign && !service)) {
          return json({ ok: false, error: "missing_required_fields" }, 400);
        }
        const routing = routeLead({ campaign, service });
        try {
          // Targeted Twenty REST filter; never create if response is ambiguous.
          const filter = encodeURIComponent(JSON.stringify({
            and: [
              { rescuExternalId: { eq: externalId } },
              { rescuSource: { eq: source } }
            ]
          }));
          const existing = await twentyFetch(env, "/rest/opportunities?filter=" + filter + "&limit=2");
          const rows = existing?.data?.opportunities ?? existing?.opportunities;
          if (!Array.isArray(rows)) return json({ ok: false, error: "lookup_shape_unknown" }, 502);
          if (rows.length) return json({ ok: true, status: "duplicate", created: false }, 200);
          const created = await twentyFetch(env, "/rest/opportunities", {
            method: "POST",
            body: JSON.stringify({
              name: "RESCU " + (service || campaign).slice(0, 60) + " inquiry",
              stage: "DISCOVERED",
              rescuExternalId: externalId,
              rescuSource: source,
              rescuCampaign: campaign,
              rescuRoutingOwner: routing.routingOwner,
              rescuAutomationState: routing.automationState,
              rescuLifecycle: "Discovered",
              rescuSuppressed: true
            })
          });
          const id = created?.data?.createOpportunity?.id ??
            created?.data?.opportunity?.id ?? created?.opportunity?.id ?? created?.id;
          if (!id) return json({ ok: false, error: "creation_unverified" }, 502);
          return json({ ok: true, created: true, id, routingOwner: routing.routingOwner });
        } catch (error) {
          return json({ ok: false, error: "twenty_intake_failed", status: error.status || 500 }, 502);
        }
      }

      if (request.method === "GET" && url.pathname === "/admin/health") {
        return json({
          ok: true,
          authorized: true,
          twentyConfigured: Boolean(env.TWENTY_API_KEY && env.TWENTY_BASE_URL),
        });
      }

      // Read-only, authenticated provisioning preview. No schema writes occur.
      if (request.method === "GET" && url.pathname === "/admin/provision/plan") {
        try {
          const objectsResponse = await twentyFetch(env, "/rest/metadata/objects");
          const fieldsResponse = await twentyFetch(env, "/rest/metadata/fields");
          const extract = (value, key) => Array.isArray(value) ? value :
            Array.isArray(value?.data) ? value.data :
            Array.isArray(value?.[key]) ? value[key] :
            Array.isArray(value?.data?.[key]) ? value.data[key] : [];
          const objects = extract(objectsResponse, "objects");
          const fields = extract(fieldsResponse, "fields");
          const opportunity = objects.find(o => o.nameSingular === "opportunity" || o.namePlural === "opportunities");
          if (!opportunity?.id || !Array.isArray(fields)) {
            return json({ ok: false, error: "metadata_shape_unrecognized", objectCount: objects.length, fieldCount: fields.length }, 502);
          }
          const desired = [
            ["rescuLifecycle", "Rescu Lifecycle", "TEXT"],
            ["rescuService", "Rescu Service", "TEXT"],
            ["rescuCampaign", "Rescu Campaign", "TEXT"],
            ["rescuSource", "Rescu Source", "TEXT"],
            ["rescuLeadScore", "Rescu Lead Score", "NUMBER"],
            ["rescuLeadTier", "Rescu Lead Tier", "TEXT"],
            ["rescuRoutingOwner", "Rescu Routing Owner", "TEXT"],
            ["rescuAutomationState", "Rescu Automation State", "TEXT"],
            ["rescuResponseState", "Rescu Response State", "TEXT"],
            ["rescuRecycleDate", "Rescu Recycle Date", "DATE"],
            ["rescuSuppressed", "Rescu Suppressed", "BOOLEAN"],
            ["rescuBookingSource", "Rescu Booking Source", "TEXT"],
            ["rescuRevenueSource", "Rescu Revenue Source", "TEXT"],
          ];
          const existing = fields.filter(field => field.objectMetadataId === opportunity.id);
          return json({
            ok: true, mode: "dry_run", writesPerformed: 0,
            opportunityObjectId: opportunity.id,
            existingFieldCount: existing.length,
            fields: desired.map(([name,label,type]) => ({
              name, label, type,
              action: existing.some(field => field.name === name) ? "exists" : "create",
            })),
            pipelineStages: ["Discovered","Qualified","Drafted","Contacted","Replied","Meeting","Booked","Won","Lost","Recycle"],
            note: "Review only; no changes to Twenty. Existing opportunity stage is not modified.",
          });
        } catch (error) {
          return json({ ok: false, error: "provision_plan_failed", status: error?.status || 500 }, 502);
        }
      }

      return json({ ok: false, error: "admin_route_not_implemented" }, 404);
    }

    return json({ ok: false, error: "not_found" }, 404);
  },
};
