from __future__ import annotations

import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client
from schwab_py_skills.env import load_schwab_credentials
from schwab_py_skills.token_info import token_summary


def main() -> int:
    creds = load_schwab_credentials()
    client = create_client(creds)
    print(json.dumps(token_summary(creds.token_path, token_age=client.token_age()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
