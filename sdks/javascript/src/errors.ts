// RFC 7807 Problem Details -> typed errors (spec chapter 8).

export interface Problem {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  request_id?: string;
  [k: string]: unknown;
}

export class OpenApiError extends Error {
  status: number;
  title: string;
  type: string;
  detail?: string;
  request_id?: string;
  instance?: string;
  raw: Problem;
  constructor(p: Problem) {
    super(`${p.status} ${p.title}: ${p.detail ?? p.type}`);
    this.name      = new.target.name;
    this.status    = p.status;
    this.title     = p.title;
    this.type      = p.type;
    this.detail    = p.detail;
    this.request_id = p.request_id as string | undefined;
    this.instance  = p.instance;
    this.raw       = p;
  }
}

export class InvalidRequest          extends OpenApiError {}   // 400
export class InvalidToken            extends OpenApiError {}   // 401
export class InsufficientScope       extends OpenApiError {}   // 403
export class NotFound                extends OpenApiError {}   // 404
export class IdempotencyConflict     extends OpenApiError {}   // 409
export class ManifestHashMismatch    extends OpenApiError {}   // 422 hash
export class ManifestFieldNotAllowed extends OpenApiError {}   // 422 field
export class RateLimited             extends OpenApiError {}   // 429
export class ServiceUnavailable      extends OpenApiError {}   // 503

const TYPE_MAP: Record<string, new (p: Problem) => OpenApiError> = {
  "manifest-hash-mismatch":     ManifestHashMismatch,
  "manifest-field-not-allowed": ManifestFieldNotAllowed,
};
const STATUS_MAP: Record<number, new (p: Problem) => OpenApiError> = {
  400: InvalidRequest,
  401: InvalidToken,
  403: InsufficientScope,
  404: NotFound,
  409: IdempotencyConflict,
  422: OpenApiError,
  429: RateLimited,
  503: ServiceUnavailable,
};

export function fromProblem(status: number, body: unknown, requestId?: string): OpenApiError {
  const p: Problem = {
    type:   "",
    title:  "",
    status,
    ...(typeof body === "object" && body !== null ? body : {}),
  } as Problem;
  if (p.status === undefined) p.status = status;
  if (requestId && !p.request_id) p.request_id = requestId;
  const suffix = p.type.includes("/") ? p.type.split("/").pop()! : p.type;
  const Cls = TYPE_MAP[suffix] ?? STATUS_MAP[status] ?? OpenApiError;
  return new Cls(p);
}
