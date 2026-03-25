# AR Language — Windows Installer
# ─────────────────────────────────────────────────────────────────
# This script installs AR Language on any Windows PC.
# Run it in PowerShell with one command:
#
#   irm https://raw.githubusercontent.com/clink9199/AR-Language/main/install.ps1 | iex
#
# What it does:
#   1. Creates  C:\Program Files\AR Language\
#   2. Downloads ar.exe from the latest GitHub release
#   3. Adds it permanently to your system PATH
# ─────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

# ── Configuration ─────────────────────────────────────────────────
$GITHUB_USER = "clink9199"
$GITHUB_REPO = "AR-Language"
$INSTALL_DIR  = "$env:LOCALAPPDATA\ARLanguage"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗"
Write-Host "  ║     AR Language — Installer V1.0     ║"
Write-Host "  ╚══════════════════════════════════════╝"
Write-Host ""

# ── Step 1: Create install directory ─────────────────────────────
Write-Host "  [1/3] Creating install directory..."
New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null

# ── Step 2: Download ar.exe ───────────────────────────────────────
Write-Host "  [2/3] Downloading ar.exe from GitHub..."
$releaseUrl = "https://github.com/$GITHUB_USER/$GITHUB_REPO/releases/latest/download/ar.exe"
$destPath   = "$INSTALL_DIR\ar.exe"

try {
    Invoke-WebRequest -Uri $releaseUrl -OutFile $destPath -UseBasicParsing
    Write-Host "        Downloaded to $destPath"
} catch {
    Write-Host ""
    Write-Host "  ERROR: Could not download ar.exe." -ForegroundColor Red
    Write-Host "  Make sure you've created a GitHub Release with ar.exe attached." -ForegroundColor Yellow
    Write-Host "  Release URL attempted: $releaseUrl" -ForegroundColor Yellow
    exit 1
}

# ── Step 3: Add to PATH ───────────────────────────────────────────
Write-Host "  [3/3] Adding to system PATH..."
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$INSTALL_DIR", "User")
    Write-Host "        PATH updated!"
} else {
    Write-Host "        Already in PATH — skipping."
}

# ── Done ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ✅ AR Language installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  Open a NEW terminal and run:"
Write-Host "       ar yourfile.ar" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To launch the interactive shell:"
Write-Host "       ar" -ForegroundColor Cyan
Write-Host ""
