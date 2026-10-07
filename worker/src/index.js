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
  // Lightweight authenticated request. This does not mutate CRM data.
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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/health")) {
      return json({
        ok: true,
        service: "rescu-growth-crm",
        twentyConfigured: Boolean(env.TWENTY_API_KEY),
        twentyBaseUrlConfigured: Boolean(env.TWENTY_BASE_URL),
      });
    }

    if (request.method === "GET" && url.pathname === "/health/twenty") {
      if (!env.TWENTY_API_KEY || !env.TWENTY_BASE_URL) {
        return json({ ok: false, connected: false, error: "twenty_not_configured" }, 503);
      }
      const result = await probeTwenty(env);
      return json({ ok: result.connected, ...result }, result.connected ? 200 : 502);
    }

    // Provisioning and synchronization endpoints are deliberately not exposed
    // until an admin authorization secret is configured. This prevents a
    // public workers.dev URL from changing CRM metadata or records.
    return json({ ok: false, error: "not_found" }, 404);
  },
};
