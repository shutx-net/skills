"""Data model for inventory items."""

from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    name: str
    quantity: int = 0

    def __post_init__(self):
        if not self.sku:
            raise ValueError("sku must not be empty")
        if self.quantity < 0:
            raise ValueError("quantity must not be negative")
