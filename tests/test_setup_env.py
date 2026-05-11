from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from schwab_py_skills.setup_env import _valid_token_path, show_env


def test_token_path_validator_requires_existing_parent(tmp_path: Path) -> None:
    assert _valid_token_path(str(tmp_path / "token.json"))
    assert not _valid_token_path(str(tmp_path / "missing" / "token.json"))


def test_show_env_does_not_expose_secret(capsys) -> None:
    env = {
        "SCHWAB_API_KEY": "abcdefghij12345",
        "SCHWAB_APP_SECRET": "secretsecret123",
        "SCHWAB_CALLBACK_URL": "https://127.0.0.1:8182/",
        "SCHWAB_TOKEN_PATH": r"C:\shared\token.json",
    }
    with patch.dict("os.environ", env, clear=True):
        show_env()

    output = capsys.readouterr().out
    assert "abcdefghij12345" not in output
    assert "SCHWAB_TOKEN_PATH" in output
