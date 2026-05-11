from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_movers


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab movers.")
    parser.add_argument("--index", required=True)
    parser.add_argument("--sort-order")
    parser.add_argument("--frequency")
    args = parser.parse_args()

    response = get_movers(
        create_client(),
        args.index,
        sort_order=args.sort_order,
        frequency=args.frequency,
    )
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
