## Start New Project

Create or refresh `HANDOFF.md` using the handoff workflow. Record timestamps,
validation status, current repo state, blockers, and exact resume commands.

## Resume Existing Project

Read `HANDOFF.md` first. Compare it with the live repo state before continuing.
Report mismatches and the immediate next steps.

## Schwab Rules

- Use `schwab-py` directly through the local Python package and scripts.
- Do not route normal Schwab work through an MCP server.
- Treat `SCHWAB_TOKEN_PATH` as user-owned shared configuration.
- Never invent a default token path, move the token, or create a replacement token
  path for convenience.
- Order workflows are dry-run-first. Live place, cancel, and replace require an
  explicit confirmation flag.
- Keep Codex skills under `.codex/skills/<skill-name>/SKILL.md`.
