// Offline test using a fetch shim. Uses node --test (built-in).
import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { TwoAfricaClient, SpecVersion } from "../src/client.ts";
import { InvalidToken, ManifestHashMismatch, RateLimited, IdempotencyConflict } from "../src/errors.ts";

type Capture = { url: string; init: RequestInit | undefined };

function shim(seq: Array<{ status: number; body?: unknown; headers?: Record<string,string> }>): { fetchImpl: typeof fetch; captures: Capture[] } {
  let i = 0;
  const captures: Capture[] = [];
  const fetchImpl = (async (url: any, init?: RequestInit) => {
    captures.push({ url: String(url), init });
    const r = seq[i++]!;
    return new Response(
      r.status === 204 ? null : JSON.stringify(r.body ?? null),
      {
        status: r.status,
        statusText: { 200: "OK", 201: "Created", 202: "Accepted", 204: "No Content" }[r.status] ?? "",
        headers: { "Content-Type": "application/json", ...(r.headers ?? {}) },
      }
    );
  }) as typeof fetch;
  return { fetchImpl, captures };
}

function mkclient(seq: any) {
  const { fetchImpl, captures } = shim(seq);
  return {
    client: new TwoAfricaClient({
      baseUrl: "https://sandbox.example",
      accessToken: "tok",
      manifestHash: "sha256:" + "0".repeat(64),
      fetchImpl,
    }),
    captures,
  };
}

describe("TwoAfricaClient", () => {

  it("healthz sends X-Spec-Version, no Authorization", async () => {
    const { client, captures } = mkclient([{ status: 200, body: { status: "ok", spec_version: SpecVersion, server_time: "x" } }]);
    const r = await client.healthz();
    assert.equal(r.status, "ok");
    const h = (captures[0]!.init?.headers ?? {}) as Record<string,string>;
    assert.equal(h["X-Spec-Version"], SpecVersion);
    assert.equal(h["Authorization"], undefined);
  });

  it("yields attaches all 4 mandatory headers + uuid Idempotency-Key", async () => {
    const { client, captures } = mkclient([{ status: 202, body: { batch_id: "b", accepted_count: 1, accepted_at: "x" } }]);
    const ack = await client.upstream.yields({ tenantPseudoId: "tpi", records: [{} as any] });
    assert.equal(ack.accepted_count, 1);
    const h = (captures[0]!.init?.headers ?? {}) as Record<string,string>;
    assert.equal(h["X-Spec-Version"], SpecVersion);
    assert.ok(h["X-Privacy-Manifest-Hash"]?.startsWith("sha256:"));
    assert.equal(h["Authorization"], "Bearer tok");
    assert.match(h["Idempotency-Key"]!, /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/);
  });

  it("yields without manifestHash throws", async () => {
    const { client } = mkclient([]);
    client.manifestHash = undefined;
    await assert.rejects(() => client.upstream.yields({ tenantPseudoId: "x", records: [] }), /X-Privacy-Manifest-Hash/);
  });

  it("422 manifest-hash-mismatch -> ManifestHashMismatch", async () => {
    const { client } = mkclient([{ status: 422, body: { type: "https://errors.2africa.ai/manifest-hash-mismatch", title: "UE", status: 422 } }]);
    await assert.rejects(() => client.upstream.yields({ tenantPseudoId: "x", records: [{} as any] }), ManifestHashMismatch);
  });

  it("401 -> InvalidToken", async () => {
    const { client } = mkclient([{ status: 401, body: { type: "x/invalid-token", title: "U", status: 401 } }]);
    await assert.rejects(() => client.downstream.dictionaries(), InvalidToken);
  });

  it("429 -> RateLimited", async () => {
    const { client } = mkclient([{ status: 429, body: { type: "x/rate-limited", title: "TM", status: 429 }, headers: { "Retry-After": "47" } }]);
    await assert.rejects(() => client.downstream.dictionaries(), RateLimited);
  });

  it("409 -> IdempotencyConflict", async () => {
    const { client } = mkclient([{ status: 409, body: { type: "x/idempotency-conflict", title: "C", status: 409 } }]);
    await assert.rejects(() => client.upstream.yields({ tenantPseudoId: "x", records: [{} as any] }), IdempotencyConflict);
  });

  it("privacy.publishManifest caches the returned hash", async () => {
    const { client } = mkclient([{ status: 200, body: { manifest_hash: "sha256:" + "a".repeat(64), accepted_at: "x" } }]);
    client.manifestHash = undefined;
    const ack = await client.privacy.publishManifest("manifest_version: 1.0.0");
    assert.equal(ack.manifest_hash, "sha256:" + "a".repeat(64));
    assert.equal(client.manifestHash, ack.manifest_hash);
  });

  it("telemetry omits Idempotency-Key, accepts 204", async () => {
    const { client, captures } = mkclient([{ status: 204 }]);
    await client.upstream.telemetry({ tenantPseudoId: "x", events: [{ event: "a.b", occurred_at: "x" }] });
    const h = (captures[0]!.init?.headers ?? {}) as Record<string,string>;
    assert.equal(h["Idempotency-Key"], undefined);
  });

});
