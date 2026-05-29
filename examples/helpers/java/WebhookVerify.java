// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - HMAC-SHA256 webhook verifier (single class, JDK 17+).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/java/WebhookVerify.java
//
// Usage in a Spring controller:
//
//   byte[] raw = StreamUtils.copyToByteArray(request.getInputStream());
//   WebhookVerify.verify(
//       System.getenv("WEBHOOK_SECRET"),
//       request.getHeader("X-AgriCloud-Signature"),
//       raw);

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class WebhookVerify {

    public static final int REPLAY_WINDOW_S = 300;

    private static final Pattern SIG_RE = Pattern.compile("^t=(\\d+),v1=([0-9a-f]{64})$");

    private WebhookVerify() {}

    public static class SignatureException extends RuntimeException {
        public SignatureException(String msg) { super(msg); }
    }

    public static void verify(String secret, String header, byte[] rawBody) {
        verify(secret, header, rawBody, Instant.now().getEpochSecond());
    }

    public static void verify(String secret, String header, byte[] rawBody, long nowEpochSec) {
        if (header == null) throw new SignatureException("missing X-AgriCloud-Signature header");
        Matcher m = SIG_RE.matcher(header.trim());
        if (!m.matches()) throw new SignatureException("malformed X-AgriCloud-Signature header");
        long ts = Long.parseLong(m.group(1));
        String suppliedHex = m.group(2);
        if (Math.abs(nowEpochSec - ts) > REPLAY_WINDOW_S) {
            throw new SignatureException("timestamp outside " + REPLAY_WINDOW_S + "s window");
        }
        byte[] expected = computeHmac(secret, ts, rawBody);
        if (!constantTimeEquals(expected, hexDecode(suppliedHex))) {
            throw new SignatureException("HMAC mismatch");
        }
    }

    private static byte[] computeHmac(String secret, long ts, byte[] body) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            mac.update((ts + ".").getBytes(StandardCharsets.UTF_8));
            mac.update(body);
            return mac.doFinal();
        } catch (Exception e) {
            throw new RuntimeException("HMAC-SHA256 unavailable on this JDK?", e);
        }
    }

    private static boolean constantTimeEquals(byte[] a, byte[] b) {
        if (a.length != b.length) return false;
        int r = 0;
        for (int i = 0; i < a.length; i++) r |= (a[i] ^ b[i]);
        return r == 0;
    }

    private static byte[] hexDecode(String s) {
        byte[] out = new byte[s.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(s.substring(2 * i, 2 * i + 2), 16);
        }
        return out;
    }

    public static void main(String[] args) {
        String secret = "whsec_demo_do_not_use_in_prod";
        byte[] raw = "{\"event_id\":\"a\"}".getBytes(StandardCharsets.UTF_8);
        long ts = Instant.now().getEpochSecond();
        String hex = bytesToHex(computeHmac(secret, ts, raw));
        verify(secret, "t=" + ts + ",v1=" + hex, raw);
        System.out.println("OK: signature verified for ts=" + ts);
    }

    private static String bytesToHex(byte[] b) {
        StringBuilder sb = new StringBuilder(b.length * 2);
        for (byte v : b) sb.append(String.format("%02x", v));
        return sb.toString();
    }
}
