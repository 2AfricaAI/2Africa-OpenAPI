// SPDX-License-Identifier: Apache-2.0
//
// 2Africa OpenAPI - Privacy Manifest canonical hash (single class, JDK 17+).
//
// Vendor by:
//   curl -O https://raw.githubusercontent.com/2AfricaAI/2Africa-OpenAPI/main/examples/helpers/java/ManifestHash.java
//
// This file accepts a manifest as a Map<String,Object> tree (the parsed
// data model). Bring your own JSON/YAML parser (Jackson, SnakeYAML, etc.)
// and pass the parsed Map in. The canonicalisation rule from spec §4.3
// is implemented here without external deps.

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public final class ManifestHash {

    private ManifestHash() {}

    public static String hash(Map<String, Object> manifest) {
        try {
            byte[] canonical = canonicalJson(manifest).getBytes(StandardCharsets.UTF_8);
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical);
            StringBuilder sb = new StringBuilder("sha256:");
            for (byte b : digest) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("SHA-256 unavailable?", e);
        }
    }

    /** RFC 8785-aligned canonical JSON: sorted keys, no whitespace. */
    public static String canonicalJson(Object node) {
        StringBuilder sb = new StringBuilder();
        encode(node, sb);
        return sb.toString();
    }

    private static void encode(Object node, StringBuilder sb) {
        if (node == null)               sb.append("null");
        else if (node instanceof Map<?,?> m) encodeMap(m, sb);
        else if (node instanceof List<?> l)  encodeList(l, sb);
        else if (node instanceof String s)   encodeString(s, sb);
        else if (node instanceof Boolean b)  sb.append(b);
        else if (node instanceof Number n)   sb.append(n.toString());
        else throw new IllegalArgumentException("Cannot encode " + node.getClass());
    }

    private static void encodeMap(Map<?,?> m, StringBuilder sb) {
        List<String> keys = new ArrayList<>();
        for (Object k : m.keySet()) {
            if (!(k instanceof String)) throw new IllegalArgumentException("non-string key");
            keys.add((String) k);
        }
        Collections.sort(keys);
        sb.append('{');
        for (int i = 0; i < keys.size(); i++) {
            if (i > 0) sb.append(',');
            encodeString(keys.get(i), sb);
            sb.append(':');
            encode(m.get(keys.get(i)), sb);
        }
        sb.append('}');
    }

    private static void encodeList(List<?> l, StringBuilder sb) {
        sb.append('[');
        for (int i = 0; i < l.size(); i++) {
            if (i > 0) sb.append(',');
            encode(l.get(i), sb);
        }
        sb.append(']');
    }

    private static void encodeString(String s, StringBuilder sb) {
        sb.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"'  -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\b' -> sb.append("\\b");
                case '\f' -> sb.append("\\f");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
                }
            }
        }
        sb.append('"');
    }

    public static void main(String[] args) {
        Map<String,Object> sample = new LinkedHashMap<>();
        sample.put("manifest_version", "1.0.0");
        sample.put("profile", "balanced");
        sample.put("generated_at", "2026-05-29T14:30:00Z");
        sample.put("owner_id", "jane.doe@example-farm.ke");
        Map<String,Object> eps = new LinkedHashMap<>();
        Map<String,Object> y = new LinkedHashMap<>();
        y.put("enabled", true);
        y.put("retention_days", 365);
        eps.put("yields", y);
        sample.put("endpoints", eps);
        System.out.println(hash(sample));
    }
}
