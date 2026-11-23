package dev.lab.orders;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OrdersApiTest {
    @LocalServerPort
    private int port;

    private RestClient http;

    @BeforeEach
    void connect() {
        http = RestClient.builder().baseUrl("http://127.0.0.1:" + port).build();
    }

    @ParameterizedTest
    @CsvSource({"4999,599", "5001,0"})
    void createsAndRetrievesStoredOrders(int subtotal, int shipping) {
        assertStoredOrder(subtotal, shipping);
    }

    @Test
    void offersFreeShippingAtThreshold() {
        assertStoredOrder(5000, 0);
    }

    private void assertStoredOrder(int subtotal, int shipping) {
        var response = http.post().uri("/api/orders").contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("subtotalCents", subtotal)).retrieve()
                .toEntity(OrderController.OrderView.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        var order = response.getBody();
        assertThat(order).isNotNull();
        assertThat(order.id()).isNotNull();
        assertThat(order.subtotalCents()).isEqualTo(subtotal);
        assertThat(order.shippingCents()).isEqualTo(shipping);
        assertThat(order.totalCents()).isEqualTo(subtotal + shipping);
        assertThat(response.getHeaders().getLocation().getPath()).isEqualTo("/api/orders/" + order.id());
        var stored = http.get().uri(response.getHeaders().getLocation()).retrieve()
                .toEntity(OrderController.OrderView.class);
        assertThat(stored.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(stored.getBody()).isEqualTo(order);
    }

    @Test
    void rejectsInvalidOrdersAndReportsMissingOrders() {
        var negative = http.post().uri("/api/orders").contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("subtotalCents", -1)).exchange((req, res) -> res.getStatusCode());
        var missingSubtotal = http.post().uri("/api/orders").contentType(MediaType.APPLICATION_JSON)
                .body(Map.of()).exchange((req, res) -> res.getStatusCode());
        var missingOrder = http.get().uri("/api/orders/{id}", UUID.randomUUID())
                .exchange((req, res) -> res.getStatusCode());
        assertThat(negative).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(missingSubtotal).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(missingOrder).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
