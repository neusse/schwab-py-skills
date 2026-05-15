from __future__ import annotations

import json
from pathlib import Path

from schwab_py_skills.token_info import token_summary


def test_token_summary_exposes_access_and_estimated_refresh_datetimes(tmp_path: Path) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text(
        json.dumps(
            {
                "creation_timestamp": 1_700_000_000,
                "token": {
                    "access_token": "access",
                    "refresh_token": "refresh",
                    "expires_at": 1_700_001_800,
                    "expires_in": 1800,
                    "scope": "api",
                },
            }
        ),
        encoding="utf-8",
    )

    summary = token_summary(token_path, token_age=60, now=1_700_000_600)

    assert summary["created_at"] == 1_700_000_000
    assert summary["created_at_datetime"] == "2023-11-14T22:13:20+00:00"
    assert summary["access_expires_at"] == 1_700_001_800
    assert summary["access_expires_at_datetime"] == "2023-11-14T22:43:20+00:00"
    assert summary["access_expires_in"] == 1800
    assert summary["refresh_expires_at_estimated"] == 1_700_604_800.0
    assert summary["refresh_expires_at_estimated_datetime"] == "2023-11-21T22:13:20+00:00"
    assert summary["refresh_expires_in_estimated"] == 604200
    assert summary["expires_in"] == 1800
    assert summary["token_age"] == 60
