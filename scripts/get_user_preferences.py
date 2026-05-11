from __future__ import annotations

import json

import _path  # noqa: F401
from schwab_py_skills.client import create_client, response_json


def main() -> int:
    print(json.dumps(response_json(create_client().get_user_preferences()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
