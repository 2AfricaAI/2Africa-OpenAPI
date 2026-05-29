// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - Lightweight JWT claims validator (single file).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/js/jwt-validate.ts
//
// This file does NOT verify the JWT signature. Pair with `jose` or `jsonwebtoken`
// for signature + JWKS handling. Here we only encode the project-specific claim
// rules (iss / aud / exp leeway / scope).
//
// Recommended pairing with `jose`:
//
//   import { jwtVerify, createRemoteJWKSet } from "jose";
//   const JWKS = createRemoteJWKSet(new URL("https://api.agricloud.2africa.ai/.well-known/jwks.json"));
//   const { payload } = await jwtVerify(token, JWKS, {
//     issuer: "https://api.agricloud.2africa.ai",
//     audience: "openapi.2africa.ai",
//   });
//   validateClaims(payload, { expectedIss: "https://api.agricloud.2africa.ai" });
//   requireScope(payload, "upstream:yields");

export const DEFAULT_LEEWAY_S = 30;
export const DEFAULT_AUD = "openapi.2africa.ai";

export class ClaimError extends Error {}

export interface ClaimOptions {
  expectedIss: string;
  expectedAud?: string;
  leewayS?: number;
  now?: number;  // epoch seconds
}

export function validateClaims(
  payload: Record<string, unknown>,
  opts: ClaimOptions
): void {
  const expectedAud = opts.expectedAud ?? DEFAULT_AUD;
  const leeway = opts.leewayS ?? DEFAULT_LEEWAY_S;
  const now = opts.now ?? Math.floor(Date.now() / 1000);

  if (payload.iss !== opts.expectedIss) {
    throw new ClaimError(`unexpected iss: ${String(payload.iss)}`);
  }
  const audValue = payload.aud;
  const auds: string[] = typeof audValue === "string"
    ? [audValue]
    : Array.isArray(audValue) ? audValue.map(String) : [];
  if (!auds.includes(expectedAud)) {
    throw new ClaimError(`aud does not include ${expectedAud}: got ${JSON.stringify(auds)}`);
  }
  const exp = payload.exp;
  if (typeof exp !== "number" || now > exp + leeway) {
    throw new ClaimError("token expired");
  }
  const iat = payload.iat;
  if (typeof iat === "number" && iat - leeway > now) {
    throw new ClaimError("token iat is in the future");
  }
  const nbf = payload.nbf;
  if (typeof nbf === "number" && nbf - leeway > now) {
    throw new ClaimError("token not yet valid (nbf)");
  }
}

export function requireScope(payload: Record<string, unknown>, scope: string): void {
  const s = payload.scope;
  if (typeof s !== "string") throw new ClaimError("scope claim missing or not a string");
  if (!s.split(" ").includes(scope)) throw new ClaimError(`missing required scope: ${scope}`);
}

if (typeof process !== "undefined" && process.argv[1]?.endsWith("jwt-validate.ts")) {
  const now = Math.floor(Date.now() / 1000);
  const sample = {
    iss: "https://api.agricloud.2africa.ai",
    aud: "openapi.2africa.ai",
    iat: now - 60,
    exp: now + 3500,
    scope: "upstream:yields privacy:manage",
  };
  validateClaims(sample, { expectedIss: "https://api.agricloud.2africa.ai" });
  requireScope(sample, "upstream:yields");
  console.log("OK: sample token passed all claim checks");
}
