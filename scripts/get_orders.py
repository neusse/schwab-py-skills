from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, get_account_hash, response_json
from schwab_py_skills.portfolio import get_orders_for_account


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab account orders.")
    parser.add_argument("--account-hash")
    parser.add_argument("--max-results", type=int)
    parser.add_argument("--from-entered-datetime")
    parser.add_argument("--to-entered-datetime")
    parser.add_argument("--status")
    args = parser.parse_args()

    client = create_client()
    account_hash = get_account_hash(client, args.account_hash)
    response = get_orders_for_account(
        client,
        account_hash,
        max_results=args.max_results,
        from_entered_datetime=args.from_entered_datetime,
        to_entered_datetime=args.to_entered_datetime,
        status=args.status,
    )
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
