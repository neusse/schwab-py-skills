param(
    [string[]]$Skills,
    [string]$Destination = "$env:USERPROFILE\.codex\skills",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$sourceRoot = Join-Path $repoRoot ".codex\skills"
if (-not (Test-Path $sourceRoot)) {
    throw "Skill source directory not found: $sourceRoot"
}

$destRoot = [System.IO.Path]::GetFullPath($Destination)
if (-not (Test-Path $destRoot) -and -not $WhatIf) {
    New-Item -ItemType Directory -Path $destRoot | Out-Null
}

$skillDirs = Get-ChildItem -Path $sourceRoot -Directory
if ($Skills -and $Skills.Count -gt 0) {
    $wanted = @{}
    foreach ($skill in $Skills) { $wanted[$skill] = $true }
    $skillDirs = $skillDirs | Where-Object { $wanted.ContainsKey($_.Name) }
    $missing = $Skills | Where-Object {
        -not (Test-Path (Join-Path $sourceRoot $_))
    }
    if ($missing) {
        throw "Requested skill(s) not found: $($missing -join ', ')"
    }
}

foreach ($dir in $skillDirs) {
    $skillFile = Join-Path $dir.FullName "SKILL.md"
    if (-not (Test-Path $skillFile)) {
        throw "Missing SKILL.md for $($dir.Name)"
    }

    $target = Join-Path $destRoot $dir.Name
    Write-Host "Deploying $($dir.Name) -> $target"
    if (-not $WhatIf) {
        if (Test-Path $target) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
        Copy-Item -LiteralPath $dir.FullName -Destination $target -Recurse
        if (-not (Test-Path (Join-Path $target "SKILL.md"))) {
            throw "Deployment verification failed for $($dir.Name)"
        }
    }
}

Write-Host "Done. Skills processed: $($skillDirs.Count)"
