"""Dataclass-based models for the 12 endpoints.

These mirror the schemas in spec/openapi.yaml but stay dependency-free
(stdlib dataclasses, no pydantic).  Use them for type hints; the client
also accepts plain dicts.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal, Any, Dict


# ---- primitives --------------------------------------------------------

@dataclass
class Money:
    amount: str
    currency: str   # ISO 4217


@dataclass
class Quantity:
    quantity: float
    unit: Literal["kg","ton","crate","bag_25kg","bag_50kg","litre","dozen","head"]


# ---- upstream records --------------------------------------------------

@dataclass
class YieldRecord:
    record_id: str
    crop_code: str
    region_code: str
    harvest_date: str   # ISO 8601 date
    quantity: Quantity
    gap_compliant: Optional[bool] = None


@dataclass
class PriceRecord:
    record_id: str
    sku_code: str
    region_code: str
    sold_on: str
    unit_price: Money
    per_unit: str


@dataclass
class GapRecord:
    record_id: str
    audit_date: str
    scheme: Literal["GLOBALG_A_P","KENYA_GAP","ORGANIC_KE","FAIRTRADE","RAINFOREST_ALLIANCE","OTHER"]
    result: Literal["pass","conditional_pass","fail"]
    non_conformities: int
    region_code: Optional[str] = None


@dataclass
class CreditPackFinancials:
    revenue: Money
    cost_of_goods: Money
    gross_profit: Money
    open_orders_value: Money


@dataclass
class CreditPackAsset:
    kind: Literal["land","equipment","livestock","inventory","other"]
    valuation: Money
    description: Optional[str] = None


@dataclass
class CreditPack:
    pack_id: str
    tenant_pseudo_id: str
    recipient_id: str
    period_start: str
    period_end: str
    financials: CreditPackFinancials
    assets: List[CreditPackAsset] = field(default_factory=list)


@dataclass
class TelemetryEvent:
    event: str
    occurred_at: str
    sdk_version: Optional[str] = None
    os: Optional[str] = None


# ---- acknowledgements --------------------------------------------------

@dataclass
class BatchAck:
    batch_id: str
    accepted_count: int
    accepted_at: str


@dataclass
class CreditPackAck:
    pack_id: str
    accepted_at: str
    delivered_to: str


@dataclass
class ManifestAck:
    manifest_hash: str
    accepted_at: str


# ---- downstream rows ---------------------------------------------------

@dataclass
class RegionalPrice:
    sku_code: str
    region_code: str
    window: Literal["7d","30d","90d"]
    p25: Money
    median: Money
    p75: Money
    sample_size: int


@dataclass
class BenchmarkMetrics:
    yield_per_hectare_kg: Optional[float] = None
    cost_per_kg: Optional[Money] = None
    gross_margin_pct: Optional[float] = None
    sample_size: int = 0


@dataclass
class Benchmark:
    region_code: str
    crop_code: str
    window: Literal["30d","90d","365d"]
    metrics: BenchmarkMetrics
    size_band: Optional[Literal["smallholder","medium","large"]] = None


@dataclass
class MarketplaceOrder:
    order_id: str
    sku_code: str
    region_code: str
    quantity: Quantity
    buyer_kind: Literal["retailer","processor","exporter","institution","other"]
    posted_at: str
    expires_at: str
    target_price: Optional[Money] = None


@dataclass
class ProcurementThreshold:
    committed: int
    required: int


@dataclass
class ProcurementOpportunity:
    opportunity_id: str
    category: Literal["seed","fertiliser","pesticide","equipment","packaging","other"]
    sku_code: str
    region_code: str
    posted_at: str
    expires_at: str
    threshold: ProcurementThreshold
    unit_price_at_threshold: Optional[Money] = None


@dataclass
class DictionaryEntry:
    code: str
    kind: Literal["crop","sku","region","unit","currency"]
    label: str
    synonyms: List[str] = field(default_factory=list)


# ---- helpers -----------------------------------------------------------

def to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses to JSON-safe dicts.  Drops None values."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_dict(v) for k, v in asdict(obj).items() if v is not None}
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items() if v is not None}
    return obj
