"""Core HTTP client.  Auto-injects mandatory headers + maps RFC 7807 errors."""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Mapping, Optional

import requests

from .errors import from_problem
from .models import (
    BatchAck, CreditPack, CreditPackAck, DictionaryEntry, ManifestAck,
    Benchmark, BenchmarkMetrics, MarketplaceOrder, ProcurementOpportunity,
    ProcurementThreshold, RegionalPrice, TelemetryEvent, YieldRecord,
    PriceRecord, GapRecord, Money, Quantity, to_dict,
)

SpecVersion = "1.0.0-rc1"


class _HttpBase:
    def __init__(self, parent: "TwoAfricaClient"):
        self._parent = parent


class _Upstream(_HttpBase):
    def yields(self, *, tenant_pseudo_id: str, records: List[YieldRecord | Dict]) -> BatchAck:
        body = {"tenant_pseudo_id": tenant_pseudo_id, "records": [to_dict(r) for r in records]}
        ack = self._parent._post("/v1/upstream/yields", body, manifest_required=True)
        return BatchAck(**ack)

    def prices(self, *, tenant_pseudo_id: str, records: List[PriceRecord | Dict]) -> BatchAck:
        body = {"tenant_pseudo_id": tenant_pseudo_id, "records": [to_dict(r) for r in records]}
        ack = self._parent._post("/v1/upstream/prices", body, manifest_required=True)
        return BatchAck(**ack)

    def gap_records(self, *, tenant_pseudo_id: str, records: List[GapRecord | Dict]) -> BatchAck:
        body = {"tenant_pseudo_id": tenant_pseudo_id, "records": [to_dict(r) for r in records]}
        ack = self._parent._post("/v1/upstream/gap-records", body, manifest_required=True)
        return BatchAck(**ack)

    def credit_pack(self, pack: CreditPack | Dict) -> CreditPackAck:
        body = to_dict(pack)
        ack = self._parent._post("/v1/upstream/credit-pack", body, manifest_required=True, expected=201)
        return CreditPackAck(**ack)

    def telemetry(self, *, tenant_pseudo_id: str, events: List[TelemetryEvent | Dict]) -> None:
        body = {"tenant_pseudo_id": tenant_pseudo_id, "events": [to_dict(e) for e in events]}
        self._parent._post(
            "/v1/upstream/telemetry", body, manifest_required=True,
            expected=204, idempotency=False,
        )


class _Downstream(_HttpBase):
    def dictionaries(self, *, kind: Optional[str] = None, page_token: Optional[str] = None,
                     page_size: int = 50) -> Dict:
        params = {"page_size": page_size}
        if kind: params["kind"] = kind
        if page_token: params["page_token"] = page_token
        return self._parent._get("/v1/downstream/dictionaries", params)

    def prices(self, *, region_code: str, sku_code: Optional[str] = None,
               window: str = "30d", page_token: Optional[str] = None,
               page_size: int = 50) -> Dict:
        params = {"region_code": region_code, "window": window, "page_size": page_size}
        if sku_code: params["sku_code"] = sku_code
        if page_token: params["page_token"] = page_token
        return self._parent._get("/v1/downstream/prices", params)

    def benchmarks(self, *, region_code: str, crop_code: str,
                   size_band: Optional[str] = None) -> Benchmark:
        params = {"region_code": region_code, "crop_code": crop_code}
        if size_band: params["size_band"] = size_band
        raw = self._parent._get("/v1/downstream/benchmarks", params)
        m = raw.get("metrics", {})
        cost = m.get("cost_per_kg")
        metrics = BenchmarkMetrics(
            yield_per_hectare_kg=m.get("yield_per_hectare_kg"),
            cost_per_kg=Money(**cost) if cost else None,
            gross_margin_pct=m.get("gross_margin_pct"),
            sample_size=m.get("sample_size", 0),
        )
        return Benchmark(
            region_code=raw["region_code"], crop_code=raw["crop_code"],
            window=raw.get("window", "90d"),
            size_band=raw.get("size_band"),
            metrics=metrics,
        )

    def marketplace(self, *, region_code: str, page_token: Optional[str] = None,
                    page_size: int = 50) -> Dict:
        params = {"region_code": region_code, "page_size": page_size}
        if page_token: params["page_token"] = page_token
        return self._parent._get("/v1/downstream/marketplace", params)

    def procurement(self, *, region_code: str, category: Optional[str] = None,
                    page_token: Optional[str] = None, page_size: int = 50) -> Dict:
        params = {"region_code": region_code, "page_size": page_size}
        if category: params["category"] = category
        if page_token: params["page_token"] = page_token
        return self._parent._get("/v1/downstream/procurement", params)


class _Privacy(_HttpBase):
    def publish_manifest(self, yaml_text: str) -> ManifestAck:
        idem = str(uuid.uuid4())
        headers = self._parent._base_headers()
        headers["Content-Type"] = "application/yaml"
        headers["Idempotency-Key"] = idem
        r = self._parent._session.put(
            self._parent.base_url + "/v1/privacy-manifest",
            data=yaml_text.encode("utf-8"),
            headers=headers,
            timeout=self._parent.timeout_s,
        )
        self._parent._raise_for_problem(r)
        body = r.json()
        # Cache the returned hash so subsequent upstream calls succeed automatically.
        self._parent.manifest_hash = body["manifest_hash"]
        return ManifestAck(**body)


class TwoAfricaClient:
    """High-level facade for the 2Africa OpenAPI."""

    def __init__(
        self,
        *,
        base_url: str,
        access_token: str,
        manifest_hash: Optional[str] = None,
        timeout_s: float = 30.0,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.manifest_hash = manifest_hash
        self.timeout_s = timeout_s
        self._session = session or requests.Session()

        self.upstream   = _Upstream(self)
        self.downstream = _Downstream(self)
        self.privacy    = _Privacy(self)

    # ---- system -------------------------------------------------------
    def healthz(self) -> Dict:
        r = self._session.get(
            self.base_url + "/healthz",
            headers={"X-Spec-Version": SpecVersion},
            timeout=self.timeout_s,
        )
        self._raise_for_problem(r)
        return r.json()

    # ---- internal -----------------------------------------------------
    def _base_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-Spec-Version": SpecVersion,
        }

    def _get(self, path: str, params: Mapping[str, Any]) -> Dict:
        r = self._session.get(
            self.base_url + path,
            headers=self._base_headers(),
            params=params,
            timeout=self.timeout_s,
        )
        self._raise_for_problem(r)
        return r.json()

    def _post(self, path: str, body: Dict, *, manifest_required: bool = False,
              expected: int = 202, idempotency: bool = True) -> Dict:
        headers = self._base_headers()
        headers["Content-Type"] = "application/json"
        if manifest_required:
            if not self.manifest_hash:
                raise RuntimeError(
                    f"Endpoint {path} requires X-Privacy-Manifest-Hash; "
                    "publish a manifest first via client.privacy.publish_manifest()"
                )
            headers["X-Privacy-Manifest-Hash"] = self.manifest_hash
        if idempotency:
            headers["Idempotency-Key"] = str(uuid.uuid4())
        r = self._session.post(
            self.base_url + path,
            data=json.dumps(body),
            headers=headers,
            timeout=self.timeout_s,
        )
        self._raise_for_problem(r)
        if r.status_code == 204:
            return {}
        return r.json()

    def _raise_for_problem(self, r: requests.Response) -> None:
        if 200 <= r.status_code < 300:
            return
        try:
            body = r.json()
        except ValueError:
            body = {"title": r.reason, "status": r.status_code, "detail": r.text[:500]}
        raise from_problem(r.status_code, body, request_id=r.headers.get("X-Request-Id"))
