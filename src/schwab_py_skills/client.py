"""Client helpers for schwab-py workflows."""

from __future__ import annotations

from typing import Any

import httpx
from schwab.auth import easy_client

from .env import SchwabCredentials, load_schwab_credentials


def create_client(credentials: SchwabCredentials | None = None) -> Any:
    """Create a schwab-py client from configured environment."""

    creds = credentials or load_schwab_credentials()
    return easy_client(
        api_key=creds.api_key,
        app_secret=creds.app_secret,
        callback_url=creds.callback_url,
        token_path=str(creds.token_path),
    )


def response_json(response: httpx.Response) -> Any:
    response.raise_for_status()
    if not response.content:
        return None
    return response.json()


def get_account_hash(client: Any, account_hash: str | None = None) -> str:
    if account_hash:
        return account_hash
    response = client.get_account_numbers()
    accounts = response_json(response)
    if not accounts:
        raise RuntimeError("No Schwab accounts returned by get_account_numbers()")
    return accounts[0]["hashValue"]
