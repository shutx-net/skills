"""Command-line interface: python -m inventory.cli --db FILE COMMAND ..."""

import argparse
import sys

from .store import InventoryStore


def build_parser():
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--db", default="inventory.json", help="path to the inventory file")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add stock")
    add.add_argument("sku")
    add.add_argument("name")
    add.add_argument("quantity", type=int)

    remove = commands.add_parser("remove", help="remove stock")
    remove.add_argument("sku")
    remove.add_argument("quantity", type=int)

    commands.add_parser("list", help="list all itmes")
    return parser


def format_item(item):
    return "{}\t{}\t{}".format(item.sku, item.name, item.quantity)


def main(argv=None, out=sys.stdout):
    args = build_parser().parse_args(argv)
    store = InventoryStore(args.db)
    if args.command == "add":
        item = store.add(args.sku, args.name, args.quantity)
        store.save()
        print(format_item(item), file=out)
    elif args.command == "remove":
        try:
            item = store.remove(args.sku, args.quantity)
        except (KeyError, ValueError) as error:
            print("error: {}".format(error), file=sys.stderr)
            return 1
        store.save()
        print(format_item(item), file=out)
    elif args.command == "list":
        for item in store.items():
            print(format_item(item), file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
