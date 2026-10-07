const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });

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

    // CRM routes will be added only after the Twenty credential is stored
    // as a Cloudflare secret. Never commit API keys to GitHub.
    return json({ ok: false, error: "not_found" }, 404);
  },
};
