from __future__ import annotations

import argparse
import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, get_account_hash, response_json
from schwab_py_skills.portfolio import get_transactions


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Schwab account transactions.")
    parser.add_argument("--account-hash")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--transaction-type")
    parser.add_argument("--symbol")
    args = parser.parse_args()

    client = create_client()
    account_hash = get_account_hash(client, args.account_hash)
    response = get_transactions(
        client,
        account_hash,
        start_date=args.start_date,
        end_date=args.end_date,
        transaction_type=args.transaction_type,
        symbol=args.symbol,
    )
    print(json.dumps(response_json(response), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
