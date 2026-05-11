---
name: schwab-auth-client
description: Use when creating or validating a schwab-py client, checking token file readiness, resolving account hashes, or diagnosing Schwab authentication setup.
---

# Schwab Auth Client

Use this skill to verify that Codex can create a `schwab-py` client directly.

## Readiness Check

```powershell
python scripts\check_auth.py
python scripts\token_info.py
```

If environment variables are missing:

```powershell
python -m schwab_py_skills.setup_env --show
python -m schwab_py_skills.setup_env
```

## Rules

- Use `schwab-py` directly, not Schwab MCP.
- Preserve `SCHWAB_TOKEN_PATH` exactly as configured.
- Prefer passing `--account-hash` when the user specifies an account.
- Redact account identifiers in summaries unless the user explicitly asks for raw output.
