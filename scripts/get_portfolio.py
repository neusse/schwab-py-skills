from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, get_account_hash, response_json
from schwab_py_skills.portfolio import get_account, get_accounts


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab account portfolio data.")
    parser.add_argument("--account-hash")
    parser.add_argument("--all-linked", action="store_true")
    parser.add_argument("--positions", action="store_true")
    args = parser.parse_args()

    client = create_client()
    if args.all_linked:
        response = get_accounts(client, positions=args.positions)
    else:
        account_hash = get_account_hash(client, args.account_hash)
        response = get_account(client, account_hash, positions=args.positions)
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
