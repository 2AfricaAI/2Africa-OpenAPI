<!--
SPDX-FileCopyrightText: 2026 2Africa AI and OpenAPI Contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# 2 · Authentication & Authorisation

## 2.1 OAuth 2.0 + PKCE

The specification uses [OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
(RFC 6749) with mandatory
[PKCE](https://datatracker.ietf.org/doc/html/rfc7636) (RFC 7636) for
all interactive flows. No homemade authentication.

Two grant types are supported:

| Grant                          | Use when                                                |
| ------------------------------ | ------------------------------------------------------- |
| `authorization_code` + PKCE    | A human is on hand to consent (initial client setup).   |
| `client_credentials`           | Headless server-to-server, scoped narrowly.             |

Both flows issue JWT access tokens (see §2.5).

## 2.2 Client registration

A client MUST be registered with the platform before it can request
tokens. Registration is out-of-band (a portal or a phone call), not
defined here.

The minimum result of registration is:

```json
{
  "client_id":      "ks_8c9d4e2f6a1b3c7d",
  "client_secret":  "<random 40+ char>",
  "redirect_uris":  ["https://farm.example.ke/oauth/callback"],
  "allowed_scopes": ["privacy:manage", "upstream:yields", "downstream:prices"],
  "issued_at":      "2026-05-15T10:00:00Z"
}
```

A platform MAY also issue a separate **webhook secret** at this stage
(see [07 Webhooks](./07-webhooks.md) §7.4).

## 2.3 Authorization Code + PKCE flow

```text
  AgriOS (client)                            Platform
  ┌──────────┐                              ┌──────────┐
  │          │ 1. GET /oauth/authorize       │          │
  │          ├──────────────────────────────►│          │
  │          │   ?client_id=...              │          │
  │          │   &redirect_uri=...           │          │
  │          │   &scope=upstream:yields ...  │          │
  │          │   &code_challenge=<S256>      │          │
  │          │   &state=<csrf>               │          │
  │          │                               │          │
  │          │ 2. user consents on platform  │          │
  │          │◄──── 302 ... ?code=<c>&state=<s> ────────┤
  │          │                               │          │
  │          │ 3. POST /oauth/token          │          │
  │          ├──────────────────────────────►│          │
  │          │   grant_type=authorization_code│         │
  │          │   code=<c>                    │          │
  │          │   code_verifier=<v>           │          │
  │          │   client_id=...               │          │
  │          │   client_secret=...           │          │
  │          │                               │          │
  │          │◄──── 200 { access_token, refresh_token } ┤
  └──────────┘                              └──────────┘
```

### 2.3.1 Authorize request

```http
GET /oauth/authorize?
  response_type=code&
  client_id=ks_8c9d4e2f6a1b3c7d&
  redirect_uri=https%3A%2F%2Ffarm.example.ke%2Foauth%2Fcallback&
  scope=upstream%3Ayields+privacy%3Amanage&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
  code_challenge_method=S256&
  state=42e0f2d7
HTTP/1.1
Host: api.agricloud.2africa.ai
```

The user lands on the platform's consent page. The page MUST list
every requested scope in plain language alongside a "what does this
mean?" hover.

### 2.3.2 Token exchange

```http
POST /oauth/token HTTP/1.1
Host: api.agricloud.2africa.ai
Content-Type: application/x-www-form-urlencoded
Authorization: Basic <base64(client_id:client_secret)>

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=https%3A%2F%2Ffarm.example.ke%2Foauth%2Fcallback
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token":  "eyJhbGciOiJSUzI1NiIs...",
  "token_type":    "Bearer",
  "expires_in":    3600,
  "refresh_token": "rt_8s2k...",
  "scope":         "upstream:yields privacy:manage"
}
```

## 2.4 Scopes

| Scope                       | Grants                                            |
| --------------------------- | ------------------------------------------------- |
| `privacy:manage`            | Publish and read the Privacy Manifest.            |
| `upstream:yields`           | POST anonymous harvest yields.                    |
| `upstream:prices`           | POST anonymous sale prices.                       |
| `upstream:gap`              | POST GAP audit records.                           |
| `upstream:credit-pack`      | POST one-shot credit packs.                       |
| `upstream:telemetry`        | POST anonymous telemetry.                         |
| `downstream:dictionaries`   | GET standard dictionaries.                        |
| `downstream:prices`         | GET regional price benchmarks.                    |
| `downstream:benchmarks`     | GET peer benchmarks.                              |
| `downstream:marketplace`    | GET buyer-posted sourcing orders.                 |
| `downstream:procurement`    | GET group-buy opportunities.                      |

Scopes are **least-privilege**. A token issued for `downstream:prices`
cannot be used to call `/v1/upstream/yields`; the server returns
`403 insufficient_scope`.

## 2.5 Access tokens are JWTs

Servers MUST issue access tokens as
[JWT](https://datatracker.ietf.org/doc/html/rfc7519) (RFC 7519). A
client should not parse the JWT (the contents are advisory only) —
but the parts are conventionally:

```json
{
  "iss":   "https://api.agricloud.2africa.ai",
  "sub":   "client:ks_8c9d4e2f6a1b3c7d",
  "aud":   "openapi.2africa.ai",
  "iat":   1748520000,
  "exp":   1748523600,
  "scope": "upstream:yields privacy:manage",
  "jti":   "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

- Algorithm MUST be `RS256` or stronger (asymmetric). `none` is
  forbidden.
- `exp - iat` SHOULD be **3600 s** (1 hour).
- Servers MUST publish their JWKS at a well-known URL (e.g.
  `/.well-known/jwks.json`).

## 2.6 Refresh tokens

- Default lifetime: **90 days**.
- **Single-use**: every refresh MUST issue a new refresh token and
  invalidate the previous one. (Rotating refresh tokens.)
- If a refresh token is presented twice, the server MUST revoke the
  entire family (this indicates token theft).

```http
POST /oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Authorization: Basic <base64(client_id:client_secret)>

grant_type=refresh_token&refresh_token=rt_8s2k...
```

## 2.7 Token revocation

Clients MUST revoke both `access_token` and `refresh_token` when the
end user disables the integration:

```http
POST /oauth/revoke HTTP/1.1
Authorization: Basic <base64(client_id:client_secret)>
Content-Type: application/x-www-form-urlencoded

token=rt_8s2k...&token_type_hint=refresh_token
```

Servers MUST treat revoked tokens as if they were expired
(`401 invalid_token`) and MUST destroy any cached sessions tied to
them within 60 seconds.

## 2.8 Client credentials flow

Used for headless server-to-server jobs (e.g. nightly telemetry
upload):

```http
POST /oauth/token HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Authorization: Basic <base64(client_id:client_secret)>

grant_type=client_credentials&scope=upstream:telemetry
```

Scopes obtainable via `client_credentials` are a subset of the
client's allowed_scopes — set at registration and announced via the
platform's OAuth metadata endpoint.

## 2.9 OAuth server metadata

Servers MUST publish [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)
metadata at:

```
/.well-known/oauth-authorization-server
```

Minimum keys:

```json
{
  "issuer":                                  "https://api.agricloud.2africa.ai",
  "authorization_endpoint":                  "https://api.agricloud.2africa.ai/oauth/authorize",
  "token_endpoint":                          "https://api.agricloud.2africa.ai/oauth/token",
  "revocation_endpoint":                     "https://api.agricloud.2africa.ai/oauth/revoke",
  "jwks_uri":                                "https://api.agricloud.2africa.ai/.well-known/jwks.json",
  "grant_types_supported":                   ["authorization_code", "client_credentials", "refresh_token"],
  "code_challenge_methods_supported":        ["S256"],
  "scopes_supported": [
    "privacy:manage",
    "upstream:yields", "upstream:prices", "upstream:gap", "upstream:credit-pack", "upstream:telemetry",
    "downstream:dictionaries", "downstream:prices", "downstream:benchmarks", "downstream:marketplace", "downstream:procurement"
  ],
  "token_endpoint_auth_methods_supported":   ["client_secret_basic"]
}
```

This metadata is what conformance test suites and SDKs hit first.
