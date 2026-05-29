// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - PKCE helper (single class, JDK 17+ only, no deps).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/java/Pkce.java
//
// Drop into your project (any package - rename the declaration). Or compile
// standalone: `javac Pkce.java && java Pkce`.

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

public final class Pkce {

    private static final int DEFAULT_VERIFIER_BYTES = 32;
    private static final SecureRandom RNG = new SecureRandom();

    private Pkce() {}

    public record Pair(String verifier, String challenge) {}

    public static Pair generate() {
        return generate(DEFAULT_VERIFIER_BYTES);
    }

    public static Pair generate(int numBytes) {
        if (numBytes < 32 || numBytes > 96) {
            throw new IllegalArgumentException(
                "numBytes must be 32..96 to keep verifier in 43..128 chars");
        }
        String verifier = generateCodeVerifier(numBytes);
        return new Pair(verifier, codeChallengeS256(verifier));
    }

    public static String generateCodeVerifier(int numBytes) {
        byte[] raw = new byte[numBytes];
        RNG.nextBytes(raw);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(raw);
    }

    public static String codeChallengeS256(String verifier) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                .digest(verifier.getBytes(StandardCharsets.US_ASCII));
            return Base64.getUrlEncoder().withoutPadding().encodeToString(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("JDK missing SHA-256? Impossible.", e);
        }
    }

    public static void main(String[] args) {
        Pair p = generate();
        System.out.println("code_verifier  = " + p.verifier());
        System.out.println("code_challenge = " + p.challenge());
        System.out.printf("  (len verifier=%d, challenge=%d)%n",
            p.verifier().length(), p.challenge().length());
    }
}
