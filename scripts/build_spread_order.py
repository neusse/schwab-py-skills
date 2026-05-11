from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.orders.strategies import iron_condor, vertical_spread


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dry-run Schwab spread order JSON.")
    parser.add_argument("--strategy", required=True, choices=["vertical", "iron-condor"])
    parser.add_argument("--long", dest="long_symbol")
    parser.add_argument("--short", dest="short_symbol")
    parser.add_argument("--put-long")
    parser.add_argument("--put-short")
    parser.add_argument("--call-short")
    parser.add_argument("--call-long")
    parser.add_argument("--contracts", required=True, type=int)
    parser.add_argument("--net-debit", type=float)
    parser.add_argument("--net-credit", type=float)
    args = parser.parse_args()

    if args.strategy == "vertical":
        if not args.long_symbol or not args.short_symbol:
            parser.error("--long and --short are required for vertical")
        order = vertical_spread(
            args.long_symbol,
            args.short_symbol,
            args.contracts,
            net_debit=args.net_debit,
            net_credit=args.net_credit,
        ).build()
    else:
        missing = [
            name
            for name in ["put_long", "put_short", "call_short", "call_long", "net_credit"]
            if getattr(args, name) is None
        ]
        if missing:
            parser.error("Missing required iron-condor args: " + ", ".join(missing))
        order = iron_condor(
            args.put_long,
            args.put_short,
            args.call_short,
            args.call_long,
            args.contracts,
            net_credit=args.net_credit,
        ).build()

    print(json.dumps(order, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
