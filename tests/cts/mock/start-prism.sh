#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Start Prism, an OpenAPI mock server, against spec/openapi.yaml.
# Useful for validating that the CTS pytest harness runs end-to-end
# without needing a live AgriCloud sandbox.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC="$SCRIPT_DIR/../../../spec/openapi.yaml"

if command -v docker >/dev/null 2>&1; then
    echo "Starting Prism via Docker on :4010 ..."
    exec docker run --rm -i -p 4010:4010 \
        -v "$SPEC:/tmp/openapi.yaml:ro" \
        stoplight/prism:5 mock -h 0.0.0.0 /tmp/openapi.yaml
elif command -v npx >/dev/null 2>&1; then
    echo "Starting Prism via npx on :4010 ..."
    exec npx -y @stoplight/prism-cli mock -h 0.0.0.0 -p 4010 "$SPEC"
else
    echo "Need docker or npx. Install one of:"
    echo "  docker pull stoplight/prism:5"
    echo "  npm install -g @stoplight/prism-cli"
    exit 1
fi
