from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_price_history


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab price history.")
    parser.add_argument("symbol")
    parser.add_argument("--period-type")
    parser.add_argument("--period")
    parser.add_argument("--frequency-type")
    parser.add_argument("--frequency")
    parser.add_argument("--start-datetime")
    parser.add_argument("--end-datetime")
    parser.add_argument("--extended-hours", action="store_true")
    parser.add_argument("--previous-close", action="store_true")
    args = parser.parse_args()

    response = get_price_history(
        create_client(),
        args.symbol,
        period_type=args.period_type,
        period=args.period,
        frequency_type=args.frequency_type,
        frequency=args.frequency,
        start_datetime=args.start_datetime,
        end_datetime=args.end_datetime,
        extended_hours=args.extended_hours or None,
        previous_close=args.previous_close or None,
    )
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
