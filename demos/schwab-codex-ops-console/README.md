# Schwab Codex Ops Console Demo

This is a static, browser-only demo that shows what Codex can build on top of
`schwab-py-skills`: charting, alert triage, option-chain interpretation,
portfolio-aware reasoning, and dry-run order planning.

It uses synthetic sample data so it is safe to share publicly. No Schwab API
credentials, account data, or live order endpoints are used by this demo.

## Start

Open the HTML file directly:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\demos\schwab-codex-ops-console\start-demo.ps1
```

Then open:

```text
http://127.0.0.1:8777
```

You can also open the HTML file directly:

```powershell
start .\demos\schwab-codex-ops-console\index.html
```

Or serve it manually:

```powershell
python -m http.server 8777 --bind 127.0.0.1 -d .\demos\schwab-codex-ops-console
```

## Stop

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\demos\schwab-codex-ops-console\stop-demo.ps1
```

If opened directly, close the browser tab. If using `python -m http.server`
manually, press `Ctrl+C` in that terminal.

## What It Demonstrates

- Schwab market-data shaped inputs becoming a decision workspace.
- Intraday charting and volume context.
- Alert ranking with explanation, confidence, and action timing.
- Option-chain interpretation around current price.
- Dry-run-first order planning that respects the repo's live-order safety model.
- Codex prompt generation for repeating each workflow against real data.
