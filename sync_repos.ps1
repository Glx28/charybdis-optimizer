<#
.SYNOPSIS
    Sync layout data across all charybdis repos after applying a new evolved layout.

.DESCRIPTION
    After applying evolved_apply.js in ZMK Studio and verifying with evolved_verify.js:
    1. Export canonical.json from ZMK Studio (zmk_studio_layout_exporter.js)
    2. Run this script to sync everything

    This script:
    - Copies canonical layout from zmk-config → optimizer
    - Copies keybindings CSV from zmk-config → coach
    - Copies layout metadata from zmk-config → coach
    - Optionally commits and pushes all repos

.PARAMETER CommitMessage
    Commit message for all repos. If omitted, only syncs files without committing.

.PARAMETER Push
    Push to remote after committing.

.EXAMPLE
    .\sync_repos.ps1
    .\sync_repos.ps1 -CommitMessage "feat: apply evolved layout research-v1" -Push
#>
param(
    [string]$CommitMessage,
    [switch]$Push
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$root\charybdis-optimizer")) {
    $root = Split-Path -Parent (Get-Location)
}

$repos = @{
    optimizer = "$root\charybdis-optimizer"
    zmkConfig = "$root\charybdis-zmk-config"
    coach     = "$root\charybdis-coach"
    tools     = "$root\charybdis-tools"
}

foreach ($name in $repos.Keys) {
    if (-not (Test-Path $repos[$name])) {
        Write-Error "Repo not found: $($repos[$name])"
        return
    }
}

Write-Host "`n=== Charybdis Layout Sync ===" -ForegroundColor Cyan

# --- Step 1: Sync canonical.json from zmk-config → optimizer ---
$zmkSource = "$($repos.zmkConfig)\config\charybdis.json"
$canonicalDest = "$($repos.optimizer)\build\canonical.json"
if (Test-Path $zmkSource) {
    Copy-Item $zmkSource $canonicalDest -Force
    Write-Host "[OK] canonical.json <- zmk-config/config/charybdis.json" -ForegroundColor Green
} else {
    Write-Host "[SKIP] zmk-config/config/charybdis.json not found" -ForegroundColor Yellow
}

# --- Step 2: Sync keybindings CSV from zmk-config → coach ---
$csvSource = "$($repos.zmkConfig)\layout\keybindings_explained.csv"
$csvDest = "$($repos.coach)\data\keybindings_explained.csv"
if (Test-Path $csvSource) {
    Copy-Item $csvSource $csvDest -Force
    Write-Host "[OK] coach/data/keybindings_explained.csv <- zmk-config" -ForegroundColor Green
} else {
    Write-Host "[SKIP] keybindings_explained.csv not found in zmk-config" -ForegroundColor Yellow
}

# --- Step 3: Sync layout_spec.json from zmk-config → coach ---
$specSource = "$($repos.zmkConfig)\layout\layout_spec.json"
$specDest = "$($repos.coach)\data\layout_spec.json"
if (Test-Path $specSource) {
    Copy-Item $specSource $specDest -Force
    Write-Host "[OK] coach/data/layout_spec.json <- zmk-config" -ForegroundColor Green
} else {
    Write-Host "[SKIP] layout_spec.json not found in zmk-config" -ForegroundColor Yellow
}

# --- Step 4: Sync charybdis_apps.json from zmk-config → coach ---
$appsSource = "$($repos.zmkConfig)\config\charybdis_apps.json"
$appsDest = "$($repos.coach)\data\charybdis_apps.json"
if (Test-Path $appsSource) {
    Copy-Item $appsSource $appsDest -Force
    Write-Host "[OK] coach/data/charybdis_apps.json <- zmk-config" -ForegroundColor Green
} else {
    Write-Host "[SKIP] charybdis_apps.json not found in zmk-config" -ForegroundColor Yellow
}

# --- Step 5: Sync windows_norwegian_host.json from zmk-config → coach ---
$hostSource = "$($repos.zmkConfig)\layout\windows_norwegian_host.json"
$hostDest = "$($repos.coach)\data\windows_norwegian_host.json"
if (Test-Path $hostSource) {
    Copy-Item $hostSource $hostDest -Force
    Write-Host "[OK] coach/data/windows_norwegian_host.json <- zmk-config" -ForegroundColor Green
} else {
    Write-Host "[SKIP] windows_norwegian_host.json not found in zmk-config" -ForegroundColor Yellow
}

# --- Report status ---
Write-Host "`n=== Git Status ===" -ForegroundColor Cyan
foreach ($name in @("optimizer", "zmkConfig", "coach", "tools")) {
    $path = $repos[$name]
    $status = git -C $path status --short 2>&1
    if ($status) {
        Write-Host "`n[$name] $path" -ForegroundColor Yellow
        Write-Host $status
    } else {
        Write-Host "`n[$name] Clean" -ForegroundColor Green
    }
}

# --- Commit and push ---
if ($CommitMessage) {
    Write-Host "`n=== Committing ===" -ForegroundColor Cyan
    foreach ($name in @("optimizer", "zmkConfig", "coach", "tools")) {
        $path = $repos[$name]
        $status = git -C $path status --short 2>&1
        if (-not $status) {
            Write-Host "[$name] Nothing to commit" -ForegroundColor DarkGray
            continue
        }
        git -C $path add -A
        git -C $path commit -m "$CommitMessage"
        Write-Host "[$name] Committed" -ForegroundColor Green

        if ($Push) {
            $branch = git -C $path branch --show-current 2>&1
            git -C $path push origin $branch 2>&1
            Write-Host "[$name] Pushed to origin/$branch" -ForegroundColor Green
        }
    }
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
