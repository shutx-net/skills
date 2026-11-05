import unittest
from datetime import date

from price_calc.coupons import Coupon


class CouponTest(unittest.TestCase):
    def setUp(self):
        self.coupon = Coupon(code="AUTUMN", percent_off=10, end_date=date(2026, 11, 30))

    def test_apply_discount(self):
        self.assertEqual(self.coupon.apply(1000, today=date(2026, 11, 1)), 900)

    def test_usable_on_end_date(self):
        self.assertEqual(self.coupon.apply(1000, today=date(2026, 11, 30)), 900)

    def test_expired_after_end_date(self):
        with self.assertRaises(ValueError):
            self.coupon.apply(1000, today=date(2026, 12, 1))


if __name__ == "__main__":
    unittest.main()
