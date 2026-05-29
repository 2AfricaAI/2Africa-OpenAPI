// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - PKCE helper (single file, no deps, browser + Node 18+).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/js/pkce.ts
//
// Uses Web Crypto (globalThis.crypto.subtle). Works in modern browsers,
// Cloudflare Workers, Deno, Bun, and Node 18+ without imports.

const DEFAULT_VERIFIER_BYTES = 32;

function base64url(bytes: Uint8Array): string {
  let str = btoa(String.fromCharCode(...bytes));
  return str.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function generateCodeVerifier(numBytes: number = DEFAULT_VERIFIER_BYTES): string {
  if (numBytes < 32 || numBytes > 96) {
    throw new Error("numBytes must be 32..96 to keep verifier in 43..128 chars");
  }
  const raw = new Uint8Array(numBytes);
  crypto.getRandomValues(raw);
  return base64url(raw);
}

export async function codeChallengeS256(verifier: string): Promise<string> {
  const data = new TextEncoder().encode(verifier);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return base64url(new Uint8Array(digest));
}

export async function generatePkcePair(numBytes?: number): Promise<{verifier: string; challenge: string}> {
  const verifier = generateCodeVerifier(numBytes);
  const challenge = await codeChallengeS256(verifier);
  return { verifier, challenge };
}

// Self-test when invoked directly via `node pkce.js` (after tsc compile) or
// `tsx pkce.ts`. Skipped when imported.
if (typeof process !== "undefined" && process.argv[1]?.endsWith("pkce.ts")) {
  generatePkcePair().then(({verifier, challenge}) => {
    console.log(`code_verifier  = ${verifier}`);
    console.log(`code_challenge = ${challenge}`);
    console.log(`  (len verifier=${verifier.length}, challenge=${challenge.length})`);
  });
}
