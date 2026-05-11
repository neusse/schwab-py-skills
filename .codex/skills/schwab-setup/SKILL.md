---
name: schwab-setup
description: Use when Schwab environment variables, token path setup, Windows persistence, or schwab-py readiness must be inspected or configured for local Codex workflows.
---

# Schwab Setup

Use this skill before live Schwab calls when credentials, callback URL, or token path may be missing.

## Commands

Inspect current settings:

```powershell
python -m schwab_py_skills.setup_env --show
```

Configure missing settings interactively:

```powershell
python -m schwab_py_skills.setup_env
```

## Rules

- `SCHWAB_TOKEN_PATH` is required and shared with other apps.
- Do not invent a default token path.
- Do not move or recreate the token file.
- Uppercase `SCHWAB_*` names are the documented interface.
- Lowercase `schwab_*` names are compatibility fallbacks only.

## Required Variables

- `SCHWAB_API_KEY`
- `SCHWAB_APP_SECRET`
- `SCHWAB_CALLBACK_URL`
- `SCHWAB_TOKEN_PATH`
