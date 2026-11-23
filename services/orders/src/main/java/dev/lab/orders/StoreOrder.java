package dev.lab.orders;

import java.util.UUID;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "store_orders")
class StoreOrder {
    @Id
    private UUID id;
    private int subtotalCents;
    private int shippingCents;

    protected StoreOrder() {}

    StoreOrder(int subtotalCents) {
        this.id = UUID.randomUUID();
        this.subtotalCents = subtotalCents;
        this.shippingCents = subtotalCents >= 5000 ? 0 : 599;
    }

    UUID id() { return id; }
    int subtotalCents() { return subtotalCents; }
    int shippingCents() { return shippingCents; }
}
