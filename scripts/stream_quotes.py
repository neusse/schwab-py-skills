from __future__ import annotations

import argparse
import asyncio

import _path  # noqa: F401
from schwab.streaming import StreamClient

from schwab_py_skills.client import create_client
from schwab_py_skills.enums import enum_list
from schwab_py_skills.streaming import stream_service


def _field_enum_for(service: str):
    return {
        "level-one-equity": StreamClient.LevelOneEquityFields,
        "level-one-option": StreamClient.LevelOneOptionFields,
    }.get(service)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stream Schwab messages for a bounded duration."
    )
    parser.add_argument(
        "--service",
        default="level-one-equity",
        choices=[
            "level-one-equity",
            "level-one-option",
            "chart-equity",
            "nasdaq-book",
            "nyse-book",
            "options-book",
            "screener-equity",
            "screener-option",
            "account-activity",
        ],
    )
    parser.add_argument("--symbols", nargs="+")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument(
        "--fields",
        nargs="+",
        help="Optional LevelOneEquityFields names, e.g. bid-price ask-price last-price total-volume.",
    )
    args = parser.parse_args()
    client = create_client()
    field_enum = _field_enum_for(args.service)
    if args.fields and field_enum is None:
        parser.error("--fields is supported for level-one-equity and level-one-option only")
    fields = enum_list(field_enum, args.fields) if field_enum is not None else None
    asyncio.run(
        stream_service(
            client,
            args.service,
            symbols=args.symbols,
            duration=args.duration,
            fields=fields,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
