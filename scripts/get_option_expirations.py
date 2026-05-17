from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_option_expirations


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab option expiration chain.")
    parser.add_argument("symbol")
    args = parser.parse_args()

    print(json.dumps(response_json(get_option_expirations(create_client(), args.symbol)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
