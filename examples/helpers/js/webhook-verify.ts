// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - HMAC-SHA256 webhook verifier (single file, Node 18+, Workers).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/js/webhook-verify.ts
//
// Usage in an Express handler:
//
//   app.use(express.raw({ type: "application/json" }));
//   app.post("/webhooks/agricloud", async (req, res) => {
//     try {
//       await verifySignature(
//         process.env.WEBHOOK_SECRET!,
//         req.header("X-AgriCloud-Signature")!,
//         req.body  // Buffer of the raw bytes
//       );
//       // ... process JSON.parse(req.body.toString())
//       res.status(202).end();
//     } catch (e) {
//       res.status(401).end();
//     }
//   });

const SIG_RE = /^t=(\d+),v1=([0-9a-f]{64})$/;
export const REPLAY_WINDOW_S = 300;

export class SignatureError extends Error {}

export async function verifySignature(
  secret: string,
  header: string,
  rawBody: Uint8Array,
  now: number = Math.floor(Date.now() / 1000)
): Promise<void> {
  const m = SIG_RE.exec(header.trim());
  if (!m) throw new SignatureError("malformed X-AgriCloud-Signature header");
  const ts = parseInt(m[1], 10);
  const suppliedHex = m[2];
  if (Math.abs(now - ts) > REPLAY_WINDOW_S) {
    throw new SignatureError(`timestamp outside ${REPLAY_WINDOW_S}s window`);
  }
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const tsPrefix = enc.encode(`${ts}.`);
  const buf = new Uint8Array(tsPrefix.length + rawBody.length);
  buf.set(tsPrefix, 0);
  buf.set(rawBody, tsPrefix.length);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", key, buf));
  const expectedHex = Array.from(sig).map(b => b.toString(16).padStart(2, "0")).join("");
  if (!constantTimeEquals(expectedHex, suppliedHex)) {
    throw new SignatureError("HMAC mismatch");
  }
}

function constantTimeEquals(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

if (typeof process !== "undefined" && process.argv[1]?.endsWith("webhook-verify.ts")) {
  const secret = "whsec_demo_do_not_use_in_prod";
  const raw = new TextEncoder().encode('{"event_id":"a"}');
  const ts = Math.floor(Date.now() / 1000);
  (async () => {
    const enc = new TextEncoder();
    const key = await crypto.subtle.importKey("raw", enc.encode(secret),
      {name:"HMAC",hash:"SHA-256"}, false, ["sign"]);
    const tsPrefix = enc.encode(`${ts}.`);
    const buf = new Uint8Array(tsPrefix.length + raw.length);
    buf.set(tsPrefix, 0); buf.set(raw, tsPrefix.length);
    const sig = new Uint8Array(await crypto.subtle.sign("HMAC", key, buf));
    const hex = Array.from(sig).map(b => b.toString(16).padStart(2, "0")).join("");
    await verifySignature(secret, `t=${ts},v1=${hex}`, raw);
    console.log(`OK: t=${ts},v1=${hex.slice(0,8)}...`);
  })();
}
