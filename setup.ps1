# SOA Deck Studio — one-time setup for Windows.
# Right-click -> "Run with PowerShell", or in a terminal:  .\setup.ps1
$ErrorActionPreference = "Stop"

Write-Host "Setting up SOA Deck Studio..." -ForegroundColor Cyan

# 1. Ensure Python 3.11+ is available
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python not found. Installing via winget..." -ForegroundColor Yellow
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
    Write-Host "Python installed. Close this window, open a NEW terminal, and run setup.ps1 again." -ForegroundColor Yellow
    exit 0
}
$version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$version -lt [version]"3.11") {
    Write-Host "Python $version found but 3.11+ is required. Please upgrade." -ForegroundColor Red
    exit 1
}

# 2. Virtual environment + install
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
& .\.venv\Scripts\python.exe -m pip install --quiet -e ".[dev]"

# 3. Health check
& .\.venv\Scripts\deckstudio.exe doctor

Write-Host ""
Write-Host "Done. To use Deck Studio, open this folder in Cursor and just ask" -ForegroundColor Green
Write-Host "for a deck — the agent knows the workflow (see README.md)." -ForegroundColor Green
