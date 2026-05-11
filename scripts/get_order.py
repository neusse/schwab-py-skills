from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, get_account_hash, response_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch one Schwab order by ID.")
    parser.add_argument("--order-id", required=True)
    parser.add_argument("--account-hash")
    args = parser.parse_args()

    client = create_client()
    account_hash = get_account_hash(client, args.account_hash)
    print(json.dumps(response_json(client.get_order(args.order_id, account_hash)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
