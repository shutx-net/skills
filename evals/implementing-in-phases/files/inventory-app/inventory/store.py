"""Inventory store backed by a JSON file."""

import json
from pathlib import Path

from .models import Item


class InventoryStore:
    def __init__(self, path):
        self.path = Path(path)
        self._items = {}
        if self.path.exists():
            for raw in json.loads(self.path.read_text(encoding="utf-8")):
                item = Item(**raw)
                self._items[item.sku] = item

    def save(self):
        data = [vars(item) for item in self.items()]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def items(self):
        """Return every item, sorted by SKU."""
        return sorted(self._items.values(), key=lambda item: item.sku)

    def get(self, sku):
        return self._items.get(sku)

    def add(self, sku, name, quantity):
        item = self._items.get(sku)
        if item is None:
            item = Item(sku=sku, name=name, quantity=quantity)
            self._items[sku] = item
        else:
            item.quantity += quantity
        return item

    def remove(self, sku, quantity):
        item = self._items.get(sku)
        if item is None:
            raise KeyError(sku)
        if quantity > item.quantity:
            raise ValueError("cannot remove {}; only {} in stock".format(quantity, item.quantity))
        item.quantity -= quantity
        return item
