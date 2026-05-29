"""
SPDX-License-Identifier: Apache-2.0

DEPRECATED PATH — kept for backwards compatibility with the v1.0.0-rc1
release. The maintained version lives at:

    examples/helpers/python/webhook_verify.py

Update your vendored copy:

    curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/python/webhook_verify.py

This file re-exports the helper for one more release. It will be
removed in v1.0.0.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "helpers", "python"))
from webhook_verify import verify_signature, SignatureError, REPLAY_WINDOW_S  # noqa: F401

if __name__ == "__main__":
    from webhook_verify import __file__ as new_path  # type: ignore
    print(f"DEPRECATED: please use {new_path}")
    # Run the new self-test
    import runpy
    runpy.run_path(new_path, run_name="__main__")
