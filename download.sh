#!/usr/bin/env bash
#
# wrapper: hame-ye mantegh dar yt_download.py ast.
#   ./download.sh                    # az videos.txt
#   ./download.sh --quality 720
#   ./download.sh --links mylist.txt
#
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# deno agar dar PATH nabashad
export PATH="$HOME/.deno/bin:$PATH"

if [ ! -x "$DIR/.venv/bin/python" ]; then
    echo "[X] venv nist. aval ./setup.sh ra ejra kon." >&2
    exit 2
fi

exec "$DIR/.venv/bin/python" "$DIR/yt_download.py" "$@"