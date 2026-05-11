from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_instruments


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Schwab instruments/fundamentals.")
    parser.add_argument("symbols", nargs="+")
    parser.add_argument("--projection", default="fundamental")
    args = parser.parse_args()

    response = get_instruments(create_client(), args.symbols, args.projection)
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
