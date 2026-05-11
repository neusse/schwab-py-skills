from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.market import get_quotes


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab quotes.")
    parser.add_argument("symbols", nargs="+")
    parser.add_argument("--fields", nargs="+", choices=["quote", "fundamental", "extended", "reference", "regular"])
    args = parser.parse_args()

    client = create_client()
    response = get_quotes(client, args.symbols, fields=args.fields)
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
