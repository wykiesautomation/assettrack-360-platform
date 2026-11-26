export default {
  async fetch(request, env) {
    const incomingUrl = new URL(request.url);
    if (request.method !== "POST" || incomingUrl.pathname !== "/api/v1/sim800l-legacy-ingest") {
      return new Response("Not found", { status: 404 });
    }
    if (!env.SIM800L_BRIDGE_SECRET) {
      return Response.json({ error: "bridge_secret_not_configured" }, { status: 503 });
    }
    const body = await request.arrayBuffer();
    const destination = "https://assettrack360.wykiesautomation.co.za/api/v1/sim800l-legacy-ingest";
    const headers = new Headers();
    headers.set("Content-Type", request.headers.get("Content-Type") || "application/json");
    headers.set("Accept", "application/json");
    for (const name of ["X-AT360-Signature", "X-Device-UID"]) {
      const value=request.headers.get(name); if (value) headers.set(name,value);
    }
    headers.set("X-AT360-Original-Host", "sim800-ingest.wykiesautomation.co.za");
    headers.set("X-AT360-Bridge", "cloudflare-sim800l-v1");
    headers.set("X-AT360-Bridge-Secret", env.SIM800L_BRIDGE_SECRET);
    const response = await fetch(destination, { method:"POST", headers, body, redirect:"manual" });
    const responseBody = await response.arrayBuffer();
    const out = new Headers();
    out.set("Content-Type", response.headers.get("Content-Type") || "application/json");
    out.set("X-AT360-Bridge", "sim800l-http-to-https-v2");
    return new Response(responseBody, { status:response.status, headers:out });
  }
};
