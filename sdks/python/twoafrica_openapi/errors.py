"""RFC 7807 Problem Details -> Python exceptions (spec chapter 8)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OpenApiError(Exception):
    """Base class for all spec errors."""
    status: int
    title: str
    type: str = ""
    detail: str = ""
    request_id: Optional[str] = None
    instance: Optional[str] = None
    raw: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.status} {self.title}: {self.detail or self.type}"


class InvalidRequest(OpenApiError):        pass   # 400
class InvalidToken(OpenApiError):          pass   # 401
class InsufficientScope(OpenApiError):     pass   # 403
class NotFound(OpenApiError):              pass   # 404
class IdempotencyConflict(OpenApiError):   pass   # 409
class ManifestHashMismatch(OpenApiError):  pass   # 422 (manifest-hash-mismatch)
class ManifestFieldNotAllowed(OpenApiError): pass # 422 (manifest-field-not-allowed)
class RateLimited(OpenApiError):           pass   # 429
class ServiceUnavailable(OpenApiError):    pass   # 503

# Map (status, type-suffix) -> Exception class
# type URLs look like https://errors.2africa.ai/<suffix>
_TYPE_MAP = {
    "manifest-hash-mismatch":     ManifestHashMismatch,
    "manifest-field-not-allowed": ManifestFieldNotAllowed,
}
_STATUS_MAP = {
    400: InvalidRequest,
    401: InvalidToken,
    403: InsufficientScope,
    404: NotFound,
    409: IdempotencyConflict,
    422: OpenApiError,  # refined by type suffix below
    429: RateLimited,
    503: ServiceUnavailable,
}


def from_problem(status: int, body: dict, request_id: Optional[str] = None) -> OpenApiError:
    """Construct the right exception subclass from a Problem body."""
    type_url = body.get("type", "") or ""
    suffix = type_url.rsplit("/", 1)[-1] if "/" in type_url else type_url
    cls = _TYPE_MAP.get(suffix) or _STATUS_MAP.get(status, OpenApiError)
    return cls(
        status=body.get("status", status),
        title=body.get("title", ""),
        type=type_url,
        detail=body.get("detail", ""),
        request_id=request_id or body.get("request_id"),
        instance=body.get("instance"),
        raw=body,
    )
