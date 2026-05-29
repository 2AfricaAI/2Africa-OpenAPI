// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - Privacy Manifest canonical hash (single file).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/js/manifest-hash.ts
//
// Pass in a parsed Manifest object (use yaml parser of choice). The
// canonicalisation rule from spec §4.3 is RFC 8785-aligned JSON with
// sorted keys + no whitespace.

function canonicalJSON(node: unknown): string {
  if (node === null || node === undefined) return "null";
  if (typeof node === "boolean" || typeof node === "number") return JSON.stringify(node);
  if (typeof node === "string") return JSON.stringify(node);
  if (Array.isArray(node)) return "[" + node.map(canonicalJSON).join(",") + "]";
  if (typeof node === "object") {
    const obj = node as Record<string, unknown>;
    const keys = Object.keys(obj).sort();
    return "{" + keys.map(k => JSON.stringify(k) + ":" + canonicalJSON(obj[k])).join(",") + "}";
  }
  throw new Error(`unencodable type: ${typeof node}`);
}

export async function hashManifest(manifest: Record<string, unknown>): Promise<string> {
  const json = canonicalJSON(manifest);
  const data = new TextEncoder().encode(json);
  const digest = await crypto.subtle.digest("SHA-256", data);
  const hex = Array.from(new Uint8Array(digest))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
  return `sha256:${hex}`;
}

if (typeof process !== "undefined" && process.argv[1]?.endsWith("manifest-hash.ts")) {
  const sample = {
    manifest_version: "1.0.0",
    profile: "balanced",
    generated_at: "2026-05-29T14:30:00Z",
    owner_id: "jane.doe@example-farm.ke",
    endpoints: { yields: { enabled: true, retention_days: 365 } },
  };
  hashManifest(sample).then(h => console.log(h));
}
