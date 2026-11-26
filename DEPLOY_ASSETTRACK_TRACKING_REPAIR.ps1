param(
    [Parameter(Mandatory=$false)]
    [string]$ZipPath = ".\AssetTrack_360_TRACKING_FINAL.zip",

    [Parameter(Mandatory=$false)]
    [string]$TargetPath = ".\assettrack-360-platform-main"
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "[AssetTrack 360] $Message" -ForegroundColor Cyan
}

$zip = (Resolve-Path $ZipPath).Path
$targetFull = [System.IO.Path]::GetFullPath($TargetPath)
$parent = Split-Path $targetFull -Parent
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = "$targetFull.backup_$stamp"
$temp = Join-Path $env:TEMP "AT360_Tracking_$stamp"

Write-Step "Validating ZIP: $zip"
if (-not (Test-Path $zip -PathType Leaf)) { throw "ZIP not found: $zip" }

New-Item -ItemType Directory -Force -Path $temp | Out-Null
Expand-Archive -LiteralPath $zip -DestinationPath $temp -Force
$source = Join-Path $temp "assettrack-360-platform-main"
if (-not (Test-Path (Join-Path $source "app\routes.py"))) {
    throw "Invalid pack. app\routes.py was not found."
}
if (-not (Test-Path (Join-Path $source "app\static\mobile_tracker.js"))) {
    throw "Invalid pack. app\static\mobile_tracker.js was not found."
}

$preserve = @(".env", ".env.production")
$preserved = @{}
if (Test-Path $targetFull) {
    foreach ($name in $preserve) {
        $candidate = Join-Path $targetFull $name
        if (Test-Path $candidate -PathType Leaf) {
            $preserved[$name] = [System.IO.File]::ReadAllBytes($candidate)
        }
    }
    Write-Step "Backing up old deployment to $backup"
    Move-Item -LiteralPath $targetFull -Destination $backup
}

try {
    Write-Step "Installing clean replacement"
    Copy-Item -LiteralPath $source -Destination $targetFull -Recurse -Force
    foreach ($name in $preserved.Keys) {
        [System.IO.File]::WriteAllBytes((Join-Path $targetFull $name), $preserved[$name])
    }
    if (-not (Test-Path (Join-Path $targetFull "app\routes.py"))) { throw "Deployment verification failed." }
    Write-Step "New tracking pack installed successfully"
    Write-Host "Target : $targetFull" -ForegroundColor Green
    if (Test-Path $backup) { Write-Host "Backup : $backup" -ForegroundColor Yellow }
    Write-Host "Next: commit/push this folder and redeploy the existing Railway service." -ForegroundColor Green
}
catch {
    Write-Host "Install failed. Restoring previous deployment." -ForegroundColor Red
    if (Test-Path $targetFull) { Remove-Item -LiteralPath $targetFull -Recurse -Force }
    if (Test-Path $backup) { Move-Item -LiteralPath $backup -Destination $targetFull }
    throw
}
finally {
    if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
