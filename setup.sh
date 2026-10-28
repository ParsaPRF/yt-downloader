#!/usr/bin/env bash
#
# nasb-e yek-bare-ye pish-niyaz-ha (ghabele ejra chand-bar)
#   chmod +x setup.sh && ./setup.sh
#
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ "$(id -u)" -ne 0 ]; then
    echo "[X] in script bayad ba root ejra shavad (sudo ./setup.sh)." >&2
    exit 1
fi

echo "[1/4] nasb-e package-haye systemi (ffmpeg, python3-venv, curl, unzip) ..."
apt update -y
apt -y install ffmpeg python3 python3-venv curl unzip

echo "[2/4] sakht-e venv va nasb-e yt-dlp ..."
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -U pip yt-dlp

echo "[3/4] nasb-e deno (JS engine baraye YouTube) ..."
export PATH="$HOME/.deno/bin:$PATH"
if ! command -v deno >/dev/null 2>&1; then
    curl -fsSL https://deno.land/install.sh | sh
    export PATH="$HOME/.deno/bin:$PATH"
fi
grep -q '.deno/bin' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH="$HOME/.deno/bin:$PATH"' >> "$HOME/.bashrc"

echo "[4/4] ejraei kardan-e script-ha ..."
chmod +x download.sh yt_download.py 2>/dev/null || true

echo
echo "[OK] nasb kamel shod."
echo "   yt-dlp version: $(.venv/bin/yt-dlp --version)"
echo "   deno version:   $(deno --version 2>/dev/null | head -n1 || echo 'VPN/network?')"
echo
echo "marhale-haye badi:"
echo "   1) link-ha ra dar videos.txt begozar:  nano videos.txt"
echo "   2) cookie ra (dar soorat-e niyaz) dar cookies.txt begozar (README_fa.md)"
echo "   3) ejra:  ./download.sh"