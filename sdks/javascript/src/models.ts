// TypeScript interfaces mirroring spec/openapi.yaml schemas.
// Bring-your-own-validation; for type-checked validation pair with `zod`.

export interface Money    { amount: string; currency: string; }
export interface Quantity { quantity: number; unit: "kg"|"ton"|"crate"|"bag_25kg"|"bag_50kg"|"litre"|"dozen"|"head"; }

export interface YieldRecord {
  record_id: string;
  crop_code: string;
  region_code: string;
  harvest_date: string;
  quantity: Quantity;
  gap_compliant?: boolean;
}

export interface PriceRecord {
  record_id: string;
  sku_code: string;
  region_code: string;
  sold_on: string;
  unit_price: Money;
  per_unit: string;
}

export interface GapRecord {
  record_id: string;
  audit_date: string;
  scheme: "GLOBALG_A_P"|"KENYA_GAP"|"ORGANIC_KE"|"FAIRTRADE"|"RAINFOREST_ALLIANCE"|"OTHER";
  result: "pass"|"conditional_pass"|"fail";
  non_conformities: number;
  region_code?: string;
}

export interface CreditPackFinancials {
  revenue: Money;
  cost_of_goods: Money;
  gross_profit: Money;
  open_orders_value: Money;
}

export interface CreditPackAsset {
  kind: "land"|"equipment"|"livestock"|"inventory"|"other";
  valuation: Money;
  description?: string;
}

export interface CreditPack {
  pack_id: string;
  tenant_pseudo_id: string;
  recipient_id: string;
  period_start: string;
  period_end: string;
  financials: CreditPackFinancials;
  assets?: CreditPackAsset[];
}

export interface TelemetryEvent {
  event: string;
  occurred_at: string;
  sdk_version?: string;
  os?: string;
}

export interface BatchAck       { batch_id: string;     accepted_count: number; accepted_at: string; }
export interface CreditPackAck  { pack_id: string;      accepted_at: string;    delivered_to: string; }
export interface ManifestAck    { manifest_hash: string; accepted_at: string; }

export interface RegionalPrice {
  sku_code: string;
  region_code: string;
  window: "7d"|"30d"|"90d";
  p25: Money; median: Money; p75: Money;
  sample_size: number;
}

export interface BenchmarkMetrics {
  yield_per_hectare_kg?: number;
  cost_per_kg?: Money;
  gross_margin_pct?: number;
  sample_size: number;
}

export interface Benchmark {
  region_code: string;
  crop_code: string;
  window: "30d"|"90d"|"365d";
  metrics: BenchmarkMetrics;
  size_band?: "smallholder"|"medium"|"large";
}

export interface MarketplaceOrder {
  order_id: string;
  sku_code: string;
  region_code: string;
  quantity: Quantity;
  target_price?: Money;
  buyer_kind: "retailer"|"processor"|"exporter"|"institution"|"other";
  posted_at: string;
  expires_at: string;
}

export interface ProcurementOpportunity {
  opportunity_id: string;
  category: "seed"|"fertiliser"|"pesticide"|"equipment"|"packaging"|"other";
  sku_code: string;
  region_code: string;
  unit_price_at_threshold?: Money;
  threshold: { committed: number; required: number };
  posted_at: string;
  expires_at: string;
}

export interface DictionaryEntry {
  code: string;
  kind: "crop"|"sku"|"region"|"unit"|"currency";
  label: string;
  synonyms?: string[];
}

export interface Page<T> { items: T[]; next_page_token?: string; }
