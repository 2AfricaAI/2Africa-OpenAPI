// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - Lightweight JWT claims validator (single class, JDK 17+).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/java/JwtValidate.java
//
// This file does NOT verify the JWT signature - pair it with a real library
// (Auth0 java-jwt, Nimbus, etc.) for signature + JWKS handling. Here we only
// encode the project-specific claim rules (iss / aud / exp leeway / scope).
//
// Recommended pairing with Auth0 java-jwt:
//
//   DecodedJWT decoded = JWT.require(algorithm).build().verify(token);
//   Map<String,Claim> claims = decoded.getClaims();
//   // Adapt the Map<String,Claim> into a Map<String,Object> for the helper.

import java.time.Instant;
import java.util.*;

public final class JwtValidate {

    public static final int DEFAULT_LEEWAY_S = 30;
    public static final String DEFAULT_AUD = "openapi.2africa.ai";

    private JwtValidate() {}

    public static class ClaimException extends RuntimeException {
        public ClaimException(String msg) { super(msg); }
    }

    public static void validateClaims(
        Map<String,Object> payload,
        String expectedIss
    ) {
        validateClaims(payload, expectedIss, DEFAULT_AUD,
            DEFAULT_LEEWAY_S, Instant.now().getEpochSecond());
    }

    public static void validateClaims(
        Map<String,Object> payload,
        String expectedIss,
        String expectedAud,
        int leewayS,
        long nowEpochSec
    ) {
        Object iss = payload.get("iss");
        if (!Objects.equals(iss, expectedIss)) {
            throw new ClaimException("unexpected iss: " + iss);
        }
        List<String> auds = new ArrayList<>();
        Object aud = payload.get("aud");
        if (aud instanceof String s) auds.add(s);
        else if (aud instanceof List<?> l) for (Object o : l) auds.add(String.valueOf(o));
        if (!auds.contains(expectedAud)) {
            throw new ClaimException("aud does not include " + expectedAud + ": got " + auds);
        }
        Number exp = (Number) payload.get("exp");
        if (exp == null || nowEpochSec > exp.longValue() + leewayS) {
            throw new ClaimException("token expired");
        }
        Number iat = (Number) payload.get("iat");
        if (iat != null && iat.longValue() - leewayS > nowEpochSec) {
            throw new ClaimException("token iat is in the future");
        }
        Number nbf = (Number) payload.get("nbf");
        if (nbf != null && nbf.longValue() - leewayS > nowEpochSec) {
            throw new ClaimException("token not yet valid (nbf)");
        }
    }

    public static void requireScope(Map<String,Object> payload, String scope) {
        Object s = payload.get("scope");
        if (!(s instanceof String str)) throw new ClaimException("scope claim missing or not a string");
        for (String part : str.split(" ")) {
            if (part.equals(scope)) return;
        }
        throw new ClaimException("missing required scope: " + scope);
    }

    public static void main(String[] args) {
        long now = Instant.now().getEpochSecond();
        Map<String,Object> sample = new HashMap<>();
        sample.put("iss", "https://api.agricloud.2africa.ai");
        sample.put("aud", "openapi.2africa.ai");
        sample.put("iat", now - 60);
        sample.put("exp", now + 3500);
        sample.put("scope", "upstream:yields privacy:manage");
        validateClaims(sample, "https://api.agricloud.2africa.ai");
        requireScope(sample, "upstream:yields");
        System.out.println("OK: sample token passed all claim checks");
    }
}
