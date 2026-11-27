// POST /api/client-intake  ·  "Let's Talk" contact form → phmconsulting.advisory@gmail.com
// Environment variables (hosting dashboard only, never in code):
//   RESEND_API_KEY  email provider API key (Resend)
//   FROM_EMAIL      authenticated sender, e.g. "PHM Website <enquiries@phmconsulting.ca>"
//   SITE_ORIGIN     https://phmconsulting.ca (comma-separate extra origins, e.g. the staging URL)
import { createHash } from "node:crypto";
import { getStore } from "@netlify/blobs";

const RECIPIENT = "phmconsulting.advisory@gmail.com"; // fixed: visitors cannot change it
const MAX_BODY = 16 * 1024;
const MIN_FILL_MS = 3000;          // spam: humans take longer than 3 seconds
const DEDUPE_HOURS = 24;

// Service names are edited by PHM in /admin, so the server accepts any short, plain service name
// (the field is still required and length-limited; it is only ever used as text in the email).
const BUDGET_OPTIONS = ["Not sure yet", "Prefer to discuss"];

const FIELDS = [ // key, email label, max, required
  ["name", "Your name", 120, true],
  ["organization", "Organization", 180, false],
  ["email", "Email address", 254, true],
  ["phone", "Phone number", 50, false],
  ["service", "How can we help?", 150, true],
  ["challenge", "What's your biggest challenge?", 3000, false],
  ["budgetAmount", "Approximate budget (CAD)", 15, false],
  ["budgetOption", "Budget", 30, false],
];

const json = (status, ok) => new Response(JSON.stringify({ ok }), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const oneLine = (s) => String(s).replace(/[\r\n]+/g, " ").trim();

export default async (req) => {
  if (req.method !== "POST") return json(405, false);
  const allowed = (process.env.SITE_ORIGIN || "").split(",").map((s) => s.trim()).filter(Boolean);
  const origin = req.headers.get("origin");
  if (!origin || (allowed.length && !allowed.includes(origin))) return json(403, false);
  if (!(req.headers.get("content-type") || "").includes("application/json")) return json(415, false);

  const raw = await req.text();
  if (new TextEncoder().encode(raw).length > MAX_BODY) return json(413, false);
  let d; try { d = JSON.parse(raw); } catch { return json(400, false); }
  if (!d || typeof d !== "object" || d.schemaVersion !== "2.0") return json(400, false);

  // Spam protection: hidden honeypot field and a minimum fill time
  if (typeof d.websiteConfirm === "string" && d.websiteConfirm.trim() !== "") return json(400, false);
  if (typeof d.elapsedMs !== "number" || d.elapsedMs < MIN_FILL_MS) return json(400, false);

  const c = {};
  for (const [k, , max, req] of FIELDS) {
    if (d[k] !== undefined && typeof d[k] !== "string") return json(400, false);
    const v = (d[k] || "").trim();
    if (req && !v) return json(400, false);
    if (v.length > max) return json(400, false);
    c[k] = v;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c.email)) return json(400, false);
  if (!c.service || /[\u0000-\u001f<>]/.test(c.service)) return json(400, false);
  if (c.budgetOption && !BUDGET_OPTIONS.includes(c.budgetOption)) return json(400, false);
  if (c.budgetAmount && c.budgetOption) return json(400, false);               // mutually exclusive
  if (c.budgetAmount && !/^\$?\s?\d{1,3}(,?\d{3})*(\.\d{1,2})?$/.test(c.budgetAmount)) return json(400, false);

  // Ignore exact repeats of the same enquiry for 24 hours
  const receivedAt = new Date().toISOString();
  const key = "dedupe/" + createHash("sha256").update(JSON.stringify(FIELDS.map(([k]) => c[k]))).digest("hex");
  let store; try { store = getStore("enquiries"); } catch { store = null; }
  if (store) {
    const seen = await store.get(key, { type: "json" }).catch(() => null);
    if (seen && Date.now() - Date.parse(seen.receivedAt) < DEDUPE_HOURS * 3600e3) return json(200, true);
  }

  const rows = FIELDS.filter(([k]) => c[k]).map(([k, label]) => [label, k === "budgetAmount" ? `CAD $${c[k].replace(/^\$\s?/, "")}` : c[k]]);
  rows.push(["Received", receivedAt]);
  const text = rows.map(([l, v]) => `${l}:\n${v}\n`).join("\n");
  const html = `<table cellpadding="8" style="font-family:Arial,sans-serif;border-collapse:collapse">${rows
    .map(([l, v]) => `<tr><td style="vertical-align:top;font-weight:bold;border-bottom:1px solid #ddd">${esc(l)}</td><td style="border-bottom:1px solid #ddd;white-space:pre-wrap">${esc(v)}</td></tr>`).join("")}</table>`;

  let sent = false;
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: process.env.FROM_EMAIL, to: [RECIPIENT], reply_to: oneLine(c.email),
        subject: oneLine(`New PHM enquiry — ${c.service}${c.organization ? " — " + c.organization : ""}`),
        text, html,
      }),
      signal: AbortSignal.timeout(15000),
    });
    sent = r.ok;
  } catch { sent = false; }
  if (!sent) { console.error("contact form: email provider did not accept the enquiry"); return json(502, false); }

  if (store) await store.setJSON(key, { receivedAt }).catch(() => {});
  return json(200, true);
};

export const config = {
  path: "/api/client-intake",
  rateLimit: { windowLimit: 5, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
