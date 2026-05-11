from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.orders.strategies import (
    bracket_order,
    covered_call,
    iron_condor,
    straddle,
    strangle,
    vertical_spread,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dry-run Schwab strategy order JSON.")
    subparsers = parser.add_subparsers(dest="strategy", required=True)

    bracket = subparsers.add_parser("bracket", help="Buy entry with OCO profit target and stop.")
    bracket.add_argument("--symbol", required=True)
    bracket.add_argument("--qty", required=True, type=int)
    bracket.add_argument("--entry-price", required=True, type=float)
    bracket.add_argument("--profit-target", required=True, type=float)
    bracket.add_argument("--stop-loss", required=True, type=float)

    vertical = subparsers.add_parser("vertical", help="Two-leg option vertical spread.")
    vertical.add_argument("--long", required=True, dest="long_symbol")
    vertical.add_argument("--short", required=True, dest="short_symbol")
    vertical.add_argument("--contracts", required=True, type=int)
    vertical.add_argument("--net-debit", type=float)
    vertical.add_argument("--net-credit", type=float)

    condor = subparsers.add_parser("iron-condor", help="Four-leg option iron condor.")
    condor.add_argument("--put-long", required=True)
    condor.add_argument("--put-short", required=True)
    condor.add_argument("--call-short", required=True)
    condor.add_argument("--call-long", required=True)
    condor.add_argument("--contracts", required=True, type=int)
    condor.add_argument("--net-credit", required=True, type=float)

    straddle_parser = subparsers.add_parser("straddle", help="Long call plus long put.")
    straddle_parser.add_argument("--call", required=True, dest="call_symbol")
    straddle_parser.add_argument("--put", required=True, dest="put_symbol")
    straddle_parser.add_argument("--contracts", required=True, type=int)
    straddle_parser.add_argument("--net-debit", required=True, type=float)

    strangle_parser = subparsers.add_parser("strangle", help="Long OTM call plus long OTM put.")
    strangle_parser.add_argument("--call", required=True, dest="call_symbol")
    strangle_parser.add_argument("--put", required=True, dest="put_symbol")
    strangle_parser.add_argument("--contracts", required=True, type=int)
    strangle_parser.add_argument("--net-debit", required=True, type=float)

    covered = subparsers.add_parser("covered-call", help="Stock buy plus short call JSON list.")
    covered.add_argument("--underlying", required=True)
    covered.add_argument("--shares", required=True, type=int)
    covered.add_argument("--call", required=True, dest="call_symbol")
    covered.add_argument("--contracts", required=True, type=int)
    covered.add_argument("--stock-limit", type=float)
    covered.add_argument("--call-limit", type=float)

    args = parser.parse_args()

    if args.strategy == "bracket":
        result = bracket_order(
            args.symbol,
            args.qty,
            args.entry_price,
            args.profit_target,
            args.stop_loss,
        ).build()
    elif args.strategy == "vertical":
        result = vertical_spread(
            args.long_symbol,
            args.short_symbol,
            args.contracts,
            net_debit=args.net_debit,
            net_credit=args.net_credit,
        ).build()
    elif args.strategy == "iron-condor":
        result = iron_condor(
            args.put_long,
            args.put_short,
            args.call_short,
            args.call_long,
            args.contracts,
            net_credit=args.net_credit,
        ).build()
    elif args.strategy == "straddle":
        result = straddle(
            args.call_symbol,
            args.put_symbol,
            args.contracts,
            net_debit=args.net_debit,
        ).build()
    elif args.strategy == "strangle":
        result = strangle(
            args.call_symbol,
            args.put_symbol,
            args.contracts,
            net_debit=args.net_debit,
        ).build()
    elif args.strategy == "covered-call":
        result = [
            order.build()
            for order in covered_call(
                args.underlying,
                args.shares,
                args.call_symbol,
                args.contracts,
                stock_limit=args.stock_limit,
                call_limit=args.call_limit,
            )
        ]
    else:
        parser.error(f"Unsupported strategy: {args.strategy}")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
