"""Discount coupons."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Coupon:
    code: str
    percent_off: int
    end_date: date

    def is_expired(self, today):
        """A coupon can still be used on its end date."""
        return today >= self.end_date

    def apply(self, amount, today):
        if self.is_expired(today):
            raise ValueError("coupon {} expired on {}".format(self.code, self.end_date.isoformat()))
        return amount - amount * self.percent_off // 100
