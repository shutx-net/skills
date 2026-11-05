import unittest

from price_calc.pricing import format_yen, subtotal


class PricingTest(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal(1200, 3), 3600)

    def test_negative_quantity_fails(self):
        with self.assertRaises(ValueError):
            subtotal(1200, -1)

    def test_format_yen(self):
        self.assertEqual(format_yen(1234567), "¥1,234,567")


if __name__ == "__main__":
    unittest.main()
