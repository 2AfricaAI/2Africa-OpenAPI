"""
twoafrica_openapi - Python SDK for the 2Africa OpenAPI v1.0 standard.

Quick start:

    from twoafrica_openapi import TwoAfricaClient

    client = TwoAfricaClient(
        base_url="https://sandbox.agricloud.2africa.ai",
        access_token=os.environ["OPENAPI_TOKEN"],
        manifest_hash=os.environ["MANIFEST_HASH"],
    )
    ack = client.upstream.yields(
        tenant_pseudo_id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
        records=[{
            "record_id": str(uuid.uuid4()),
            "crop_code": "TOMATO",
            "region_code": "KE-30",
            "harvest_date": "2026-05-20",
            "quantity": {"quantity": 1234.5, "unit": "kg"},
        }],
    )
    print(ack.accepted_count)

For helpers (PKCE, manifest hash, webhook verify, JWT validate), see the
zero-dep helpers in the spec repo's examples/helpers/python/.
"""
from .client    import TwoAfricaClient, SpecVersion
from .errors    import OpenApiError, InvalidToken, InsufficientScope, \
                       ManifestHashMismatch, RateLimited, IdempotencyConflict
from .models    import (
    Money, Quantity, BatchAck, YieldRecord, PriceRecord, GapRecord,
    CreditPack, TelemetryEvent, RegionalPrice, Benchmark,
)

__all__ = [
    "TwoAfricaClient", "SpecVersion",
    "OpenApiError", "InvalidToken", "InsufficientScope",
    "ManifestHashMismatch", "RateLimited", "IdempotencyConflict",
    "Money", "Quantity", "BatchAck", "YieldRecord", "PriceRecord",
    "GapRecord", "CreditPack", "TelemetryEvent", "RegionalPrice", "Benchmark",
]

__version__ = "1.0.0-rc1"
