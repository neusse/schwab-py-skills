"""Portfolio and account wrappers over schwab-py client methods."""

from __future__ import annotations

from typing import Any

from schwab.client import Client

from .datetime_utils import parse_datetime
from .enums import clean_none, enum_value


def get_account(client: Any, account_hash: str, *, positions: bool = False) -> Any:
    fields = client.Account.Fields.POSITIONS if positions else None
    return client.get_account(account_hash, fields=fields)


def get_accounts(client: Any, *, positions: bool = False) -> Any:
    fields = client.Account.Fields.POSITIONS if positions else None
    return client.get_accounts(fields=fields)


def get_transactions(
    client: Any,
    account_hash: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    transaction_type: str | None = None,
    symbol: str | None = None,
) -> Any:
    kwargs = clean_none(
        {
            "start_date": parse_datetime(start_date),
            "end_date": parse_datetime(end_date),
            "transaction_types": enum_value(Client.Transactions.TransactionType, transaction_type),
            "symbol": symbol,
        }
    )
    return client.get_transactions(account_hash, **kwargs)


def get_orders_for_account(
    client: Any,
    account_hash: str,
    *,
    max_results: int | None = None,
    from_entered_datetime: str | None = None,
    to_entered_datetime: str | None = None,
    status: str | None = None,
) -> Any:
    kwargs = clean_none(
        {
            "max_results": max_results,
            "from_entered_datetime": parse_datetime(from_entered_datetime),
            "to_entered_datetime": parse_datetime(to_entered_datetime),
            "status": enum_value(Client.Order.Status, status),
        }
    )
    return client.get_orders_for_account(account_hash, **kwargs)
