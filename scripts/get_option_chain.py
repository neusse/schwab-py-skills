from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_option_chain


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab option chain data.")
    parser.add_argument("symbol")
    parser.add_argument("--contract-type", choices=["call", "put", "all"])
    parser.add_argument("--strike-count", type=int)
    parser.add_argument("--strategy")
    parser.add_argument("--strike", type=float)
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--include-underlying-quote", action="store_true")
    args = parser.parse_args()

    response = get_option_chain(
        create_client(),
        args.symbol,
        contract_type=args.contract_type,
        strike_count=args.strike_count,
        strategy=args.strategy,
        strike=args.strike,
        from_date=args.from_date,
        to_date=args.to_date,
        include_underlying_quote=args.include_underlying_quote or None,
    )
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
