from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, get_account_hash
from schwab_py_skills.orders.executor import load_order_file, preview_order


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview a Schwab order without placing it.")
    parser.add_argument("--order-file", required=True)
    parser.add_argument("--account-hash")
    args = parser.parse_args()

    client = create_client()
    account_hash = get_account_hash(client, args.account_hash)
    result = preview_order(client, account_hash, load_order_file(args.order_file))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
