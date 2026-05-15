param(
    [int]$Port = 8778
)

$ErrorActionPreference = "Stop"
$DemoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidPath = Join-Path $DemoRoot ".demo-server.pid"
$PortPath = Join-Path $DemoRoot ".demo-server.port"

if (Test-Path -LiteralPath $PidPath) {
    $ExistingPid = Get-Content -LiteralPath $PidPath -Raw
    $ExistingProcess = Get-Process -Id ([int]$ExistingPid) -ErrorAction SilentlyContinue
    if ($ExistingProcess) {
        $ExistingPort = if (Test-Path -LiteralPath $PortPath) { Get-Content -LiteralPath $PortPath -Raw } else { $Port }
        Write-Host "Demo server already running at http://127.0.0.1:$ExistingPort"
        exit 0
    }
    Remove-Item -LiteralPath $PidPath -Force
}

$PortBusy = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($PortBusy) {
    throw "Port $Port is already in use. Rerun with -Port <free-port>."
}

$ServerPath = Join-Path $DemoRoot "server.py"
$Arguments = @("`"$ServerPath`"", "--host", "127.0.0.1", "--port", "$Port")
$Process = Start-Process -FilePath "python" -ArgumentList $Arguments -PassThru -WindowStyle Hidden
$Process.Id | Set-Content -LiteralPath $PidPath -Encoding ascii
$Port | Set-Content -LiteralPath $PortPath -Encoding ascii

Write-Host "Live demo server started at http://127.0.0.1:$Port"
Write-Host "Stop it with: powershell.exe -ExecutionPolicy Bypass -File `"$DemoRoot\stop-demo.ps1`""
