# Schwab Codex Live Demo

This is the live counterpart to the static ops-console demo. It keeps the same
browser experience, but the data comes from real `schwab-py-skills` calls:

- `get_quotes`
- `get_price_history`
- `get_option_chain`
- local dry-run bracket JSON generation

It is intentionally read-only. The server exposes market-data and local analysis
only. It does not expose Schwab order preview, place, cancel, or replace routes.

## Start

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\demos\schwab-codex-live-demo\start-demo.ps1
```

Then open:

```text
http://127.0.0.1:8778
```

## Stop

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\demos\schwab-codex-live-demo\stop-demo.ps1
```

## Requirements

The same Schwab environment used by the skills must be ready:

- `SCHWAB_API_KEY`
- `SCHWAB_APP_SECRET`
- `SCHWAB_CALLBACK_URL`
- `SCHWAB_TOKEN_PATH`

The demo server imports this repo's Python package from `src`, so it works from a
repo checkout without requiring a separate install.

## API

The browser calls one read-only endpoint:

```text
/api/context?symbol=AAPL
```

The response contains compact quote data, 5-day chart points, the nearest option
expiration around spot, Codex-style decision context, and local dry-run JSON.
