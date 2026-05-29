// Core HTTP client. Auto-injects mandatory headers + maps RFC 7807 errors.

import { fromProblem } from "./errors.ts";
import type {
  BatchAck, Benchmark, CreditPack, CreditPackAck, DictionaryEntry,
  GapRecord, ManifestAck, MarketplaceOrder, Page, PriceRecord,
  ProcurementOpportunity, RegionalPrice, TelemetryEvent, YieldRecord,
} from "./models.ts";

export const SpecVersion = "1.1.0-rc1";

export interface TwoAfricaClientOptions {
  baseUrl: string;
  accessToken: string;
  manifestHash?: string;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;   // injectable for tests / Workers
}

function uuidv4(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // RFC 4122 v4 fallback
  const b = new Uint8Array(16);
  crypto.getRandomValues(b);
  b[6] = (b[6]! & 0x0f) | 0x40;
  b[8] = (b[8]! & 0x3f) | 0x80;
  const h = Array.from(b, x => x.toString(16).padStart(2, "0")).join("");
  return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`;
}

export class TwoAfricaClient {
  baseUrl: string;
  accessToken: string;
  manifestHash?: string;
  timeoutMs: number;
  private fetch: typeof fetch;

  readonly upstream:   UpstreamAPI;
  readonly downstream: DownstreamAPI;
  readonly privacy:    PrivacyAPI;
  readonly events:     EventsAPI;
  readonly marketplaceResponses: MarketplaceResponsesAPI;

  constructor(opts: TwoAfricaClientOptions) {
    this.baseUrl      = opts.baseUrl.replace(/\/+$/, "");
    this.accessToken  = opts.accessToken;
    this.manifestHash = opts.manifestHash;
    this.timeoutMs    = opts.timeoutMs ?? 30_000;
    this.fetch        = opts.fetchImpl ?? fetch.bind(globalThis);

    this.upstream   = new UpstreamAPI(this);
    this.downstream = new DownstreamAPI(this);
    this.privacy    = new PrivacyAPI(this);
    this.events     = new EventsAPI(this);
    this.marketplaceResponses = new MarketplaceResponsesAPI(this);
  }

  async healthz(): Promise<{ status: "ok"|"degraded"; spec_version: string; server_time: string }> {
    const r = await this.fetch(`${this.baseUrl}/healthz`, {
      headers: { "X-Spec-Version": SpecVersion },
    });
    await this.raiseForProblem(r);
    return r.json() as Promise<any>;
  }

  baseHeaders(): Record<string,string> {
    return {
      Authorization:   `Bearer ${this.accessToken}`,
      "X-Spec-Version": SpecVersion,
    };
  }

  async get<T = unknown>(path: string, params: Record<string, string|number|undefined>): Promise<T> {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) qs.set(k, String(v));
    }
    const r = await this.fetch(`${this.baseUrl}${path}?${qs}`, { headers: this.baseHeaders() });
    await this.raiseForProblem(r);
    return r.json() as Promise<T>;
  }

  async post<T = unknown>(
    path: string,
    body: unknown,
    opts: { manifestRequired?: boolean; expected?: number; idempotency?: boolean } = {}
  ): Promise<T> {
    const headers: Record<string,string> = { ...this.baseHeaders(), "Content-Type": "application/json" };
    if (opts.manifestRequired) {
      if (!this.manifestHash) {
        throw new Error(
          `Endpoint ${path} requires X-Privacy-Manifest-Hash; ` +
          "publish a manifest first via client.privacy.publishManifest()"
        );
      }
      headers["X-Privacy-Manifest-Hash"] = this.manifestHash;
    }
    if (opts.idempotency !== false) headers["Idempotency-Key"] = uuidv4();
    const r = await this.fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    await this.raiseForProblem(r);
    if (r.status === 204) return {} as T;
    return r.json() as Promise<T>;
  }

  async raiseForProblem(r: Response): Promise<void> {
    if (r.ok) return;
    let body: unknown;
    try { body = await r.json(); }
    catch { body = { title: r.statusText, status: r.status }; }
    throw fromProblem(r.status, body, r.headers.get("X-Request-Id") ?? undefined);
  }
}

// ---- subresources ------------------------------------------------------

export class UpstreamAPI {
  private c: TwoAfricaClient;
  constructor(c: TwoAfricaClient) { this.c = c; }
  yields(args:     { tenantPseudoId: string; records: YieldRecord[] }): Promise<BatchAck> {
    return this.c.post("/v1/upstream/yields",      { tenant_pseudo_id: args.tenantPseudoId, records: args.records }, { manifestRequired: true });
  }
  prices(args:     { tenantPseudoId: string; records: PriceRecord[] }): Promise<BatchAck> {
    return this.c.post("/v1/upstream/prices",      { tenant_pseudo_id: args.tenantPseudoId, records: args.records }, { manifestRequired: true });
  }
  gapRecords(args: { tenantPseudoId: string; records: GapRecord[] }): Promise<BatchAck> {
    return this.c.post("/v1/upstream/gap-records", { tenant_pseudo_id: args.tenantPseudoId, records: args.records }, { manifestRequired: true });
  }
  creditPack(pack: CreditPack): Promise<CreditPackAck> {
    return this.c.post("/v1/upstream/credit-pack", pack, { manifestRequired: true, expected: 201 });
  }
  telemetry(args:  { tenantPseudoId: string; events: TelemetryEvent[] }): Promise<void> {
    return this.c.post(
      "/v1/upstream/telemetry",
      { tenant_pseudo_id: args.tenantPseudoId, events: args.events },
      { manifestRequired: true, expected: 204, idempotency: false }
    ) as Promise<void>;
  }
}

export class DownstreamAPI {
  private c: TwoAfricaClient;
  constructor(c: TwoAfricaClient) { this.c = c; }
  dictionaries(args: { kind?: string; pageToken?: string; pageSize?: number } = {}): Promise<Page<DictionaryEntry>> {
    return this.c.get("/v1/downstream/dictionaries", { kind: args.kind, page_token: args.pageToken, page_size: args.pageSize ?? 50 });
  }
  prices(args: { regionCode: string; skuCode?: string; window?: "7d"|"30d"|"90d"; pageToken?: string; pageSize?: number }): Promise<Page<RegionalPrice>> {
    return this.c.get("/v1/downstream/prices",       { region_code: args.regionCode, sku_code: args.skuCode, window: args.window ?? "30d", page_token: args.pageToken, page_size: args.pageSize ?? 50 });
  }
  benchmarks(args: { regionCode: string; cropCode: string; sizeBand?: "smallholder"|"medium"|"large" }): Promise<Benchmark> {
    return this.c.get("/v1/downstream/benchmarks",   { region_code: args.regionCode, crop_code: args.cropCode, size_band: args.sizeBand });
  }
  marketplace(args: { regionCode: string; pageToken?: string; pageSize?: number }): Promise<Page<MarketplaceOrder>> {
    return this.c.get("/v1/downstream/marketplace",  { region_code: args.regionCode, page_token: args.pageToken, page_size: args.pageSize ?? 50 });
  }
  procurement(args: { regionCode: string; category?: string; pageToken?: string; pageSize?: number }): Promise<Page<ProcurementOpportunity>> {
    return this.c.get("/v1/downstream/procurement",  { region_code: args.regionCode, category: args.category, page_token: args.pageToken, page_size: args.pageSize ?? 50 });
  }
}

export class PrivacyAPI {
  private c: TwoAfricaClient;
  constructor(c: TwoAfricaClient) { this.c = c; }
  async publishManifest(yamlText: string): Promise<ManifestAck> {
    const idem = uuidv4();
    const r = await (this.c as any).fetch(`${this.c.baseUrl}/v1/privacy-manifest`, {
      method: "PUT",
      headers: {
        ...this.c.baseHeaders(),
        "Content-Type": "application/yaml",
        "Idempotency-Key": idem,
      },
      body: yamlText,
    });
    await this.c.raiseForProblem(r);
    const ack = await r.json() as ManifestAck;
    this.c.manifestHash = ack.manifest_hash;
    return ack;
  }
}


export class EventsAPI {
  private c: TwoAfricaClient;
  constructor(c: TwoAfricaClient) { this.c = c; }
  since(args: { since: number; eventType?: string; pageToken?: string; pageSize?: number }): Promise<{ items: any[]; next_page_token?: string }> {
    return this.c.get("/v1/events", {
      since: args.since,
      event_type: args.eventType,
      page_token: args.pageToken,
      page_size:  args.pageSize ?? 50,
    });
  }
}

export class MarketplaceResponsesAPI {
  private c: TwoAfricaClient;
  constructor(c: TwoAfricaClient) { this.c = c; }
  respond(args: {
    orderId: string;
    sellerPseudoId: string;
    offeredQuantity:  { quantity: number; unit: string };
    offeredUnitPrice: { amount: string; currency: string };
    availableFrom:  string;
    availableUntil: string;
    notes?: string;
  }): Promise<{ response_id: string; order_id: string; accepted_at: string; buyer_notified: boolean }> {
    const body: Record<string, unknown> = {
      seller_pseudo_id:   args.sellerPseudoId,
      offered_quantity:   args.offeredQuantity,
      offered_unit_price: args.offeredUnitPrice,
      available_from:     args.availableFrom,
      available_until:    args.availableUntil,
    };
    if (args.notes !== undefined) body.notes = args.notes;
    return this.c.post(
      `/v1/downstream/marketplace/${encodeURIComponent(args.orderId)}/responses`,
      body,
      { manifestRequired: false, expected: 201 }
    );
  }
}
