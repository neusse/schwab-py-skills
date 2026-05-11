from __future__ import annotations

import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json
from schwab_py_skills.env import load_schwab_credentials


def main() -> int:
    creds = load_schwab_credentials(require_token_exists=True)
    client = create_client(creds)
    accounts = response_json(client.get_account_numbers())
    print(
        json.dumps(
            {
                "token_path": str(creds.token_path),
                "token_exists": creds.token_path.exists(),
                "account_count": len(accounts or []),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
