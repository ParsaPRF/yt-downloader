# refresh-cookies.ps1
# Export YouTube cookies from a local browser and upload them to the server.
# This runs on WINDOWS, not on the server.
#
# Requirements:
#   1) yt-dlp installed on Windows:   winget install yt-dlp.yt-dlp
#   2) Logged into youtube.com in that browser (prefer a secondary account)
#   3) Optional: passwordless SSH key so this can run unattended
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File refresh-cookies.ps1
#   powershell -ExecutionPolicy Bypass -File refresh-cookies.ps1 -Browser firefox -Server root@1.2.3.4

param(
    [string]$Browser    = "chrome",
    [string]$Server     = "root@CHANGE_ME_TO_SERVER_IP",
    [string]$RemotePath = "/root/yt-downloader/cookies.txt",
    [string]$YtDlp      = "yt-dlp"
)

$ErrorActionPreference = "Stop"
$out = Join-Path $env:USERPROFILE "cookies.txt"

Write-Host "Exporting cookies from browser: $Browser ..."
& $YtDlp --cookies-from-browser $Browser --cookies $out `
    --skip-download --simulate "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 2>$null

if (-not (Test-Path $out)) {
    throw "[X] Cookie export failed (is the browser open and logged in? is the path right?)"
}

$hasLogin = Select-String -Path $out -Pattern "LOGIN_INFO|SID" -Quiet
Write-Host "   login cookies present: $hasLogin"

Write-Host "Uploading to server: $Server ..."
scp $out "${Server}:${RemotePath}"

Write-Host "[OK] Done. Cookies on the server are up to date."
