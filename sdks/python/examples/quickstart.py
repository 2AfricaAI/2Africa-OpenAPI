"""Run a full end-to-end smoke against the sandbox.

Requires:
    pip install twoafrica-openapi PyYAML
    export OPENAPI_TOKEN=<JWT from /oauth/token>
"""
from __future__ import annotations
import os, uuid, sys, pathlib

from twoafrica_openapi import TwoAfricaClient
from twoafrica_openapi.models import YieldRecord, Quantity

def main() -> int:
    token = os.environ.get("OPENAPI_TOKEN")
    if not token:
        print("set OPENAPI_TOKEN to a JWT from /oauth/token", file=sys.stderr)
        return 1

    client = TwoAfricaClient(
        base_url="https://sandbox.agricloud.2africa.ai",
        access_token=token,
    )

    # 1. healthz (no auth needed in theory, but we use the client for convenience)
    print("healthz:", client.healthz())

    # 2. publish the balanced preset manifest
    manifest_path = pathlib.Path(__file__).parent.parent.parent.parent / "examples" / "manifests" / "balanced.yaml"
    with open(manifest_path) as f:
        ack = client.privacy.publish_manifest(f.read())
    print("manifest_hash:", ack.manifest_hash)

    # 3. submit one harvest record
    ack = client.upstream.yields(
        tenant_pseudo_id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
        records=[YieldRecord(
            record_id=str(uuid.uuid4()),
            crop_code="TOMATO",
            region_code="KE-30",
            harvest_date="2026-05-20",
            quantity=Quantity(quantity=1234.5, unit="kg"),
        )],
    )
    print("yields ack:", ack)

    # 4. read regional prices
    page = client.downstream.prices(region_code="KE-30", sku_code="TOMATO_GRADE_A")
    print(f"prices page: {len(page['items'])} rows")

    return 0

if __name__ == "__main__":
    sys.exit(main())
