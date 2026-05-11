from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab option expiration chain.")
    parser.add_argument("symbol")
    args = parser.parse_args()

    print(json.dumps(response_json(create_client().get_option_expiration_chain(args.symbol)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
