from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from schwab_py_skills.env import SchwabEnvError, load_schwab_credentials


def test_loads_uppercase_token_path_without_defaulting() -> None:
    env = {
        "SCHWAB_API_KEY": "upperkey123",
        "SCHWAB_APP_SECRET": "uppersecret123",
        "SCHWAB_CALLBACK_URL": "https://127.0.0.1:8182/",
        "SCHWAB_TOKEN_PATH": r"C:\shared\token.json",
    }
    with patch.dict(os.environ, env, clear=True):
        creds = load_schwab_credentials()

    assert str(creds.token_path) == r"C:\shared\token.json"


def test_lowercase_fallback_is_supported() -> None:
    env = {
        "schwab_api_key": "lowerkey123",
        "schwab_app_secret": "lowersecret123",
        "schwab_callback_url": "https://127.0.0.1:8182/",
        "schwab_token_path": "token.json",
    }
    with patch.dict(os.environ, env, clear=True):
        creds = load_schwab_credentials()

    assert str(creds.token_path) == "token.json"


def test_missing_token_path_raises_required_name() -> None:
    env = {
        "SCHWAB_API_KEY": "upperkey123",
        "SCHWAB_APP_SECRET": "uppersecret123",
        "SCHWAB_CALLBACK_URL": "https://127.0.0.1:8182/",
    }
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(SchwabEnvError, match="SCHWAB_TOKEN_PATH"):
            load_schwab_credentials()
