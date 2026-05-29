#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Regenerate a strict, Pydantic-validated client from spec/openapi.yaml.
# The output goes into ./generated/ and lives alongside the hand-written
# twoafrica_openapi/ package.

set -euo pipefail

SPEC=../../spec/openapi.yaml
OUT=./generated

if ! command -v openapi-generator-cli >/dev/null 2>&1; then
    echo "openapi-generator-cli not on PATH."
    echo "Install one of:"
    echo "  npm install -g @openapitools/openapi-generator-cli"
    echo "  brew install openapi-generator"
    echo "  pip install openapi-generator-cli"
    exit 1
fi

rm -rf "$OUT"
openapi-generator-cli generate \
    -i "$SPEC" \
    -g python \
    -o "$OUT" \
    --additional-properties=packageName=twoafrica_openapi_generated,projectName=twoafrica-openapi-generated,packageVersion=1.0.0rc1

echo
echo "Generated client at $OUT/twoafrica_openapi_generated/"
echo "Add it as an optional dep in pyproject.toml or import alongside the hand-written client."
