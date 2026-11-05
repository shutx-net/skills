import tempfile
import unittest
from pathlib import Path

from inventory.store import InventoryStore


class InventoryStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "inventory.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_new_and_existing_item(self):
        store = InventoryStore(self.path)
        store.add("A-1", "Bolt", 5)
        item = store.add("A-1", "Bolt", 3)
        self.assertEqual(item.quantity, 8)

    def test_remove_more_than_in_stock_fails(self):
        store = InventoryStore(self.path)
        store.add("A-1", "Bolt", 2)
        with self.assertRaises(ValueError):
            store.remove("A-1", 3)

    def test_save_and_reload(self):
        store = InventoryStore(self.path)
        store.add("B-2", "Nut", 4)
        store.save()
        self.assertEqual(InventoryStore(self.path).get("B-2").quantity, 4)

    def test_items_are_sorted_by_sku(self):
        store = InventoryStore(self.path)
        store.add("C-3", "Washer", 1)
        store.add("A-1", "Bolt", 1)
        self.assertEqual([item.sku for item in store.items()], ["A-1", "C-3"])


if __name__ == "__main__":
    unittest.main()
