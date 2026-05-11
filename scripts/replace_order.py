from __future__ import annotations

import argparse

import _path  # noqa: F401
from schwab_py_skills.client import create_client, get_account_hash
from schwab_py_skills.orders.executor import load_order_file, replace_order


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace a Schwab order from JSON.")
    parser.add_argument("--order-id", required=True)
    parser.add_argument("--order-file", required=True)
    parser.add_argument("--account-hash")
    parser.add_argument("--confirm-live-order", action="store_true")
    args = parser.parse_args()

    client = create_client()
    account_hash = get_account_hash(client, args.account_hash)
    replace_order(
        client,
        account_hash,
        args.order_id,
        load_order_file(args.order_file),
        confirm_live_order=args.confirm_live_order,
    )
    print("order replace submitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
