# Schwab-Py Skills Handoff

Last Updated Local: 2026-05-15 13:31 PDT
Last Updated UTC: 2026-05-15T20:31:51Z
Stale After Hours: 24
Staleness: FRESH

## Project

- Path: repo root for this checkout, for example
  `%USERPROFILE%\Codex_Projects\schwab-py-skills` on Windows.
- Git: initialized on branch `master`
- Remote: `https://github.com/neusse/schwab-py-skills`
- Published visibility: public
- Purpose: Codex-first Schwab skills and local Python utilities using `schwab-py`
  directly, not Schwab MCP.

## Current State

- Repo scaffold created with Python package under `src/schwab_py_skills`.
- Editable package installed locally with `python -m pip install -e .[dev]`.
- Market-data, portfolio, order, token, and bounded streaming commands are
  implemented.
- Codex-level user documentation is available at `docs/CODEX_SKILL_USAGE.md`.
- Deeper order strategy examples are available at `docs/ORDER_STRATEGY_EXAMPLES.md`.
- Local skill deployment docs are available at `docs/DEPLOYMENT.md`, with
  inventory in `SKILLS_INVENTORY.md`.
- README has a repo-local SVG hero banner at
  `docs/assets/schwab-py-skills-banner.svg`.
- README now leads with the Codex skills catalog, capability table, and
  `/schwab-*` usage model before Python package installation details.
- `scripts\build_strategy_order.py` builds bracket, vertical, iron condor,
  straddle, strangle, and covered-call dry-run JSON.
- `scripts\deploy-skills.ps1` deploys project skills to the local Codex skill
  directory. Dry-run validation passed; global deployment has not been executed.
- Documentation and code avoid hard-coded user-specific `C:\Users\<name>` paths.
  Use `%USERPROFILE%`, `$env:USERPROFILE`, or repo-relative paths instead.
- Initial public push completed on `master` at commit `7996eb6`.
- Live read-only smoke checks passed for `get_quotes.py AAPL MSFT`,
  `stream_quotes.py --symbols AAPL MSFT --duration 3 --fields bid-price ask-price last-price`,
  `stream_quotes.py --service account-activity --duration 1`, and `token_info.py`.
- Project skills live under `.codex/skills`.
- Setup utility is vendored locally as `python -m schwab_py_skills.setup_env`.
- Order workflows are dry-run-first and require explicit confirmation for live
  place/cancel/replace.
- `SCHWAB_TOKEN_PATH` is required and preserved exactly as user configuration.
- Token status reporting now shows token creation time, access-token expiration
  time, and estimated refresh-token expiration time. The refresh estimate is
  derived from Schwab token creation time plus seven days because the token file
  does not store a separate refresh-token expiration field.
- `charts/MSFT_120d_daily_bars.png` is included as a tracked chart artifact.
- A static browser demo now lives at
  `demos/schwab-codex-ops-console`. It presents a simulated Codex trading ops
  console with charting, alert triage, options context, decision reasoning, and
  dry-run order planning. Start it with:
  `powershell.exe -ExecutionPolicy Bypass -File .\demos\schwab-codex-ops-console\start-demo.ps1`.
- A read-only live demo now lives at `demos/schwab-codex-live-demo`. It serves a
  local browser UI on port `8778` and backs `/api/context?symbol=AAPL` with real
  `schwab-py-skills` quote, 5-day history, and option-chain calls. The live demo
  does not expose order preview, place, cancel, or replace routes.

## Validation

Run after changes:

```powershell
python -m compileall src scripts tests
python -m pytest
python -m ruff check .
```

Last full validation: passed on 2026-05-15 13:31 PDT.

## Resume Steps

1. Verify repo state:
   ```powershell
   git status --short
   ```
2. Re-run validation commands above.
3. For live readiness, inspect environment:
   ```powershell
   python -m schwab_py_skills.setup_env --show
   python scripts\check_auth.py
   ```
4. Optional: deploy skills globally after review:
   ```powershell
   pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1
   ```

## Open Risks

- Live order mutation has not been exercised; preview before any placement.
- Advanced order payloads should be previewed with Schwab before placement.

## Change Log

- 2026-05-15: Added a separate read-only live demo backed by real
  `schwab-py-skills` market-data calls and local dry-run JSON generation.
- 2026-05-15: Added the static Schwab Codex Ops Console demo with Windows
  start/stop scripts, README launch instructions, and root README visibility.
- 2026-05-14: Added datetime-rich token status output for access-token and
  estimated refresh-token lifecycle reporting, plus regression coverage and
  Codex usage documentation.
- 2026-05-11: Implemented planned market, portfolio, order, token, and streaming
  code; validation and live read-only smoke checks passed.
- 2026-05-11: Added comprehensive Codex-level usage documentation for all
  project skills.
- 2026-05-11: Added executable strategy-order examples plus local Codex skill
  deployment tooling and inventory.
- 2026-05-11: Replaced hard-coded user-specific Windows paths in docs and
  handoff with current-user or repo-relative references.
- 2026-05-11: Published repo publicly to GitHub at
  `https://github.com/neusse/schwab-py-skills`.
- 2026-05-11: Added README hero banner and badge section.
- 2026-05-12: Updated README to present the repo as a Codex skills library first,
  with skill capabilities and example `/schwab-*` prompts before Python usage.
- 2026-05-11: Initial scaffold for schwab-py Codex skills library; validation passed.
