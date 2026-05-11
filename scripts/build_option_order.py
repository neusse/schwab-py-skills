from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.orders.templates import option_order


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run Schwab option order JSON.")
    parser.add_argument(
        "--action",
        required=True,
        choices=["buy-to-open", "sell-to-close", "sell-to-open", "buy-to-close"],
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--contracts", required=True, type=int)
    parser.add_argument("--limit", type=float)
    args = parser.parse_args()

    order = option_order(args.action, args.symbol, args.contracts, args.limit).build()
    print(json.dumps(order, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
