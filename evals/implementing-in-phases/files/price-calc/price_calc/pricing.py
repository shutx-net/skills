"""Price calculations. Amounts are integers in yen."""


def subtotal(unit_price, quantity):
    if unit_price < 0 or quantity < 0:
        raise ValueError("unit_price and quantity must not be negative")
    return unit_price * quantity


def format_yen(amount):
    return "¥{:,}".format(amount)
