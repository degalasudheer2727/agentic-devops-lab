package dev.lab.orders;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OrdersApiTest {
    @Autowired
    private TestRestTemplate http;

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
        var response = http.postForEntity("/api/orders", Map.of("subtotalCents", subtotal),
                OrderController.OrderView.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        var order = response.getBody();
        assertThat(order).isNotNull();
        assertThat(order.id()).isNotNull();
        assertThat(order.subtotalCents()).isEqualTo(subtotal);
        assertThat(order.shippingCents()).isEqualTo(shipping);
        assertThat(order.totalCents()).isEqualTo(subtotal + shipping);
        assertThat(response.getHeaders().getLocation().getPath()).isEqualTo("/api/orders/" + order.id());
        var stored = http.getForEntity(response.getHeaders().getLocation(), OrderController.OrderView.class);
        assertThat(stored.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(stored.getBody()).isEqualTo(order);
    }

    @Test
    void rejectsInvalidOrdersAndReportsMissingOrders() {
        assertThat(http.postForEntity("/api/orders", Map.of("subtotalCents", -1), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(http.postForEntity("/api/orders", Map.of(), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(http.getForEntity("/api/orders/" + UUID.randomUUID(), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
