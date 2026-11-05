"""Command-line interface: python -m price_calc.cli quote UNIT_PRICE QUANTITY"""

import argparse
import sys

from .pricing import format_yen, subtotal


def build_parser():
    parser = argparse.ArgumentParser(prog="price-calc")
    commands = parser.add_subparsers(dest="command", required=True)
    quote = commands.add_parser("quote", help="show the price for a quantity")
    quote.add_argument("unit_price", type=int)
    quote.add_argument("quantity", type=int)
    return parser


def main(argv=None, out=sys.stdout):
    args = build_parser().parse_args(argv)
    if args.command == "quote":
        print(format_yen(subtotal(args.unit_price, args.quantity)), file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
