package dev.lab.orders;

import java.util.UUID;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@RestController
@RequestMapping("/api/orders")
class OrderController {
    private final OrderRepository orders;

    OrderController(OrderRepository orders) {
        this.orders = orders;
    }

    @PostMapping
    ResponseEntity<OrderView> create(@Valid @RequestBody CreateOrder request) {
        StoreOrder order = orders.save(new StoreOrder(request.subtotalCents()));
        var location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(order.id()).toUri();
        return ResponseEntity.created(location).body(OrderView.from(order));
    }

    @GetMapping("/{id}")
    ResponseEntity<OrderView> find(@PathVariable UUID id) {
        return ResponseEntity.of(orders.findById(id).map(OrderView::from));
    }

    record CreateOrder(@NotNull @PositiveOrZero @Max(100000000) Integer subtotalCents) {}

    record OrderView(UUID id, int subtotalCents, int shippingCents, int totalCents) {
        static OrderView from(StoreOrder order) {
            return new OrderView(order.id(), order.subtotalCents(), order.shippingCents(),
                    order.subtotalCents() + order.shippingCents());
        }
    }
}
