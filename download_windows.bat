@echo off
cd /d "%~dp0"
echo ============================================
echo    YouTube Downloader  (Windows)
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [!] Setup not done. Run setup_windows.ps1 first.
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" yt_download.py %*

echo.
echo Done. Press any key to close.
pause >nul
