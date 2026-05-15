$ErrorActionPreference = "Stop"
$DemoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidPath = Join-Path $DemoRoot ".demo-server.pid"
$PortPath = Join-Path $DemoRoot ".demo-server.port"

if (-not (Test-Path -LiteralPath $PidPath)) {
    Write-Host "No demo server PID file found."
    exit 0
}

$ServerPid = [int](Get-Content -LiteralPath $PidPath -Raw)
$ProcessInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $ServerPid" -ErrorAction SilentlyContinue

if ($ProcessInfo -and $ProcessInfo.CommandLine -like "*http.server*" -and $ProcessInfo.CommandLine -like "*schwab-codex-ops-console*") {
    Stop-Process -Id $ServerPid -Force
    Write-Host "Stopped demo server process $ServerPid."
} else {
    Write-Host "PID $ServerPid is not the expected demo server."
}

Remove-Item -LiteralPath $PidPath -Force
if (Test-Path -LiteralPath $PortPath) {
    Remove-Item -LiteralPath $PortPath -Force
}
