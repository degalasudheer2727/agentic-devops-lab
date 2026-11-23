"""Shipping rules for the sample storefront."""


def shipping_cost(subtotal_cents: int) -> int:
    if subtotal_cents < 0:
        raise ValueError("subtotal cannot be negative")
    return 0 if subtotal_cents >= 5000 else 599
