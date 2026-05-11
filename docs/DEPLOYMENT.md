# Deployment

This repo uses project-local Codex skills under `.codex/skills`. Deployment
copies those skills into the local Codex skill directory so they can be used
outside this repo as installed personal skills.

## Dry Run

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1 -WhatIf
```

## Deploy All Skills

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1
```

Default destination:

```text
%USERPROFILE%\.codex\skills
```

## Deploy Selected Skills

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1 -Skills schwab-market-data,schwab-orders
```

## Verify

```powershell
Test-Path "$env:USERPROFILE\.codex\skills\schwab-market-data\SKILL.md"
Test-Path "$env:USERPROFILE\.codex\skills\schwab-orders\SKILL.md"
```

## Notes

- Deployment replaces the target skill folder with the repo version.
- It does not touch `.system`, bundled, or plugin-provided skills.
- Keep this repo as the source of truth and redeploy after changing project
  skills.
