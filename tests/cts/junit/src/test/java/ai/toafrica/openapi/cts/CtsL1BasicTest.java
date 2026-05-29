// SPDX-License-Identifier: Apache-2.0
package ai.toafrica.openapi.cts;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.Duration;
import org.junit.jupiter.api.*;

@Tag("l1")
public class CtsL1BasicTest {

    static final String BASE = System.getProperty("test.base.url",
        System.getenv().getOrDefault("CTS_BASE_URL", "http://localhost:4010"));
    static final String TOKEN = System.getProperty("test.access.token",
        System.getenv().getOrDefault("CTS_ACCESS_TOKEN", ""));
    static final String SPEC_VERSION = "1.0.0-rc1";
    static final HttpClient client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(30)).build();

    @Test
    @DisplayName("L1.1 healthz returns 200 with spec_version + server_time")
    void healthzReturnsOk() throws Exception {
        HttpResponse<String> r = client.send(
            HttpRequest.newBuilder(URI.create(BASE + "/healthz"))
                .header("X-Spec-Version", SPEC_VERSION)
                .GET().build(),
            BodyHandlers.ofString());
        Assertions.assertEquals(200, r.statusCode(), r.body());
        Assertions.assertTrue(r.body().contains("\"spec_version\""));
        Assertions.assertTrue(r.body().contains("\"server_time\""));
    }

    @Test
    @DisplayName("L1.2 OAuth metadata exposes RFC 8414 fields (if implemented)")
    void oauthMetadataPresent() throws Exception {
        HttpResponse<String> r = client.send(
            HttpRequest.newBuilder(URI.create(BASE + "/.well-known/oauth-authorization-server"))
                .GET().build(),
            BodyHandlers.ofString());
        if (r.statusCode() == 404) {
            Assumptions.abort("OAuth metadata endpoint not implemented");
        }
        Assertions.assertEquals(200, r.statusCode(), r.body());
        Assertions.assertTrue(r.body().contains("\"issuer\""));
        Assertions.assertTrue(r.body().contains("\"S256\""));
    }
}
