# setup_windows.ps1
# One-time setup for the YouTube downloader on Windows.
# Installs: yt-dlp (venv) + ffmpeg + deno
#
# Run:
#   powershell -ExecutionPolicy Bypass -File setup_windows.ps1
# Or right-click -> Run with PowerShell

$ErrorActionPreference = "Continue"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $dir

Write-Host "=== Python check ===" -ForegroundColor Cyan
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[X] Python not found. Install Python 3.10+ from python.org and re-run." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}
python --version

Write-Host ""
Write-Host "=== venv + yt-dlp ===" -ForegroundColor Cyan
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -U yt-dlp
.\.venv\Scripts\yt-dlp.exe --version

Write-Host ""
Write-Host "=== ffmpeg ===" -ForegroundColor Cyan
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "ffmpeg is already available."
} elseif (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing ffmpeg via winget ..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
} else {
    Write-Host "[!] winget not found. Install ffmpeg manually (gyan.dev) and add to PATH." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== deno (YouTube JS engine) ===" -ForegroundColor Cyan
if (Get-Command deno -ErrorAction SilentlyContinue) {
    Write-Host "deno is already available."
} else {
    Write-Host "Installing deno ..."
    irm https://deno.land/install.ps1 | iex
    $env:Path += ";" + $env:USERPROFILE + "\.deno\bin"
}

Write-Host ""
Write-Host "[OK] Setup finished." -ForegroundColor Green
Write-Host "Next: put links in videos.txt, then run download_windows.bat"
Read-Host "Press Enter to close"
