from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.orders.templates import equity_order


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run Schwab equity order JSON.")
    parser.add_argument("--side", required=True, choices=["buy", "sell", "sell-short", "buy-to-cover"])
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--qty", required=True, type=int)
    parser.add_argument("--type", required=True, choices=["market", "limit"])
    parser.add_argument("--price", type=float)
    args = parser.parse_args()

    order = equity_order(args.side, args.symbol, args.qty, args.type, args.price).build()
    print(json.dumps(order, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
