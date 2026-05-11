from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_market_hours


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab market hours.")
    parser.add_argument("--markets", nargs="+", default=["equity", "option"])
    parser.add_argument("--date")
    args = parser.parse_args()

    response = get_market_hours(create_client(), args.markets, args.date)
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
