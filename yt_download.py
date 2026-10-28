#!/usr/bin/env python3
"""yt-downloader / Python version.

* link-ha ra az videos.txt mikhanad (tak-video ya playlist)
* har playlist ra be **link-haye taki** baz mikonad va har kodam ra
  dar yek khat joda dar haman file minevisad
* har video ra joda ba keyfiyat 1080p (ya balatarin mojood) hamrah seda download mikonad
* zirnevis englisi (dasti + khodkar) ra migirad
* har link **movafagh** ra belafasele az videos.txt hazf mikonad ta dar ejraye bad
  faghat link-haye namovafagh bemanand
* moghavem: edame-ye download, try mojadad, cookie, deno/EJS

nemune:
    python yt_download.py
    python yt_download.py --quality 720
    python yt_download.py --no-expand            # playlist ra baz nakon
    python yt_download.py --no-remove-links      # link-ha ra hazf nakon
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from urllib.parse import parse_qs, urlparse

DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------- #
# tools
# --------------------------------------------------------------------------- #

def is_playlist_url(url: str) -> bool:
    try:
        return "list" in parse_qs(urlparse(url).query)
    except Exception:  # noqa: BLE001
        return "list=" in url


def setup_logging(logs_dir: str) -> logging.Logger:
    os.makedirs(logs_dir, exist_ok=True)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(logs_dir, f"ytdl_{stamp}.log")
    logger = logging.getLogger("yt_downloader")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.info("log: %s", log_path)
    return logger


def find_ytdlp() -> str:
    candidates = [
        os.path.join(DIR, ".venv", "bin", "yt-dlp"),          # Linux
        os.path.join(DIR, ".venv", "Scripts", "yt-dlp.exe"),   # Windows
        os.path.join(DIR, ".venv", "Scripts", "yt-dlp"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    found = shutil.which("yt-dlp")
    if found:
        return found
    raise SystemExit("[X] yt-dlp peyda nashod. aval setup (Linux) ya setup_windows.ps1 (Windows) ra ejra kon.")


def find_ffmpeg_location() -> str | None:
    here = [
        os.path.join(DIR, "ffmpeg.exe"),
        os.path.join(DIR, "bin", "ffmpeg.exe"),
        os.path.join(DIR, "ffmpeg"),
        os.path.join(DIR, "bin", "ffmpeg"),
    ]
    for c in here:
        if os.path.isfile(c):
            return os.path.dirname(c)
    found = shutil.which("ffmpeg")
    if found:
        return os.path.dirname(found)
    return None


def load_lines(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.readlines()


def write_lines(path: str, lines: list[str]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    os.replace(tmp, path)


def iter_urls(lines: list[str]):
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s and not s.startswith("#"):
            yield i, s


def common_args(args: argparse.Namespace) -> list[str]:
    cmd: list[str] = []
    if getattr(args, "cookies_from_browser", None):
        cmd += ["--cookies-from-browser", args.cookies_from_browser]
    elif args.cookies and os.path.exists(args.cookies):
        cmd += ["--cookies", args.cookies]
    cmd += ["--remote-components", "ejs:github"]
    if shutil.which("deno") or os.path.exists(os.path.expanduser("~/.deno/bin/deno")):
        cmd += ["--js-runtimes", "deno"]
    ff = find_ffmpeg_location()
    if ff:
        cmd += ["--ffmpeg-location", ff]
    return cmd


# --------------------------------------------------------------------------- #
# baz kardan-e playlist be link-haye taki
# --------------------------------------------------------------------------- #

def expand_playlist(ytdlp: str, url: str, args: argparse.Namespace, logger: logging.Logger) -> list[str]:
    cmd = [ytdlp, "--flat-playlist", "--ignore-errors", "--no-warnings",
           "--print", "%(url)s", *common_args(args), url]
    logger.info("  baz kardan-e playlist ...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as exc:  # noqa: BLE001
        logger.warning("  baz kardan-e playlist namovafagh: %s", exc)
        return []
    urls: list[str] = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if line.startswith("http"):
            if is_playlist_url(line):
                continue
            urls.append(line)
    # hazf-e tekrari-ha ba hefz-e tartib
    seen: set[str] = set()
    unique: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    logger.info("  %s link taki peyda shod.", len(unique))
    return unique


def expand_all_playlists(path: str, lines: list[str], ytdlp: str,
                         args: argparse.Namespace, logger: logging.Logger) -> list[str]:
    if args.no_expand:
        return lines

    out: list[str] = []
    existing_urls = {u for _, u in iter_urls(lines)}

    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            out.append(raw if raw.endswith("\n") else raw + "\n")
            continue
        if is_playlist_url(s):
            expanded = expand_playlist(ytdlp, s, args, logger)
            if expanded:
                for u in expanded:
                    if u not in existing_urls:
                        out.append(u + "\n")
                        existing_urls.add(u)
                logger.info("  playlist be link-haye taki tabdil shod.")
                continue
            logger.warning("  playlist baz nashod; khat-e asli hefz mishavad.")
        out.append(raw if raw.endswith("\n") else raw + "\n")

    return out


# --------------------------------------------------------------------------- #
# download-e yek video
# --------------------------------------------------------------------------- #

def download_one(ytdlp: str, url: str, args: argparse.Namespace, logger: logging.Logger) -> bool:
    fmt = f"bv*[height<={args.quality}]+ba/b[height<={args.quality}]/bv*+ba/b"
    out_tmpl = os.path.join(args.output_dir, "%(title)s", "%(title)s.%(ext)s")
    cmd = [
        ytdlp,
        "--format", fmt,
        "--merge-output-format", "mp4",
        *common_args(args),
        "--retries", "10",
        "--fragment-retries", "10",
        "--retry-sleep", "exp=2:30",
        "--concurrent-fragments", "4",
        "--sleep-requests", "1",
        "--download-archive", args.archive,
        "--no-overwrites",
        "--embed-metadata",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", args.subs_langs,
        "--convert-subs", "srt",
        "--output", out_tmpl,
        url,
    ]
    # amdan --ignore-errors nemidahim ta code-e khoruj neshane-ye movafaghiyat bashad
    res = subprocess.run(cmd)
    return res.returncode == 0


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="YouTube downloader: playlist ra be link-haye taki tabdil mikonad va movafagh-ha ra az list hazf mikonad"
    )
    p.add_argument("--links", default=os.path.join(DIR, "videos.txt"), help="file-e link-ha")
    p.add_argument("links_pos", nargs="?", default=None, help="(ekhtiari) masir-e file-e link-ha")
    p.add_argument("--output-dir", default=os.path.join(DIR, "downloads"), help="poshe-ye khoruji")
    p.add_argument("--archive", default=os.path.join(DIR, "archive.txt"), help="file-e archive")
    p.add_argument("--cookies", default=os.path.join(DIR, "cookies.txt"), help="file-e cookie")
    p.add_argument("--cookies-from-browser", default=None,
                   help="khandan-e cookie az marurgar-e mahali (chrome/edge/firefox/brave/...) - monaseb baraye Windows")
    p.add_argument("--logs-dir", default=os.path.join(DIR, "logs"), help="poshe-ye log")
    p.add_argument("--quality", type=int, default=1080, help="hadaksar-e ertefa (pishfarz 1080)")
    p.add_argument("--subs-langs", default="en.*", help="zaban-e zirnevis (pishfarz en.*)")
    p.add_argument("--no-expand", action="store_true", help="playlist ra be link-e taki tabdil nakon")
    p.add_argument("--no-remove-links", action="store_true", help="link-haye movafagh ra az list hazf nakon")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.links_pos:
        args.links = args.links_pos
    logger = setup_logging(args.logs_dir)
    ytdlp = find_ytdlp()

    if not os.path.exists(args.links):
        logger.error("file-e link-ha peyda nashod: %s", args.links)
        return 2

    os.makedirs(args.output_dir, exist_ok=True)

    # phase 1: baz kardan-e playlist-ha be link-haye taki va neveshtan dar file
    lines = load_lines(args.links)
    if not args.no_expand:
        logger.info("phase 1: barrasi va baz kardan-e playlist-ha ...")
        lines = expand_all_playlists(args.links, lines, ytdlp, args, logger)
        write_lines(args.links, lines)
        logger.info("list be-rooz-resani shod (link-haye taki).")

    # phase 2: download-e tak-tak va hazf-e movafagh-ha
    lines = load_lines(args.links)
    entries = list(iter_urls(lines))
    if not entries:
        logger.info("hich linki dar %s baghi namande.", args.links)
        return 0

    logger.info("phase 2: download-e %s link ...", len(entries))
    removed: set[int] = set()
    ok, fail = 0, 0

    for n, (lineno, url) in enumerate(entries, 1):
        logger.info("=== [%s/%s] %s ===", n, len(entries), url)
        try:
            success = download_one(ytdlp, url, args, logger)
        except Exception as exc:  # noqa: BLE001
            logger.error("error-e ejraye yt-dlp: %s", exc)
            success = False

        if success:
            ok += 1
            if not args.no_remove_links:
                removed.add(lineno)
                write_lines(args.links, [ln for i, ln in enumerate(lines) if i not in removed])
                logger.info("link-e movafagh az list hazf shod.")
        else:
            fail += 1
            logger.warning("download namovafagh; link dar list mimanad: %s", url)

    logger.info("=" * 50)
    logger.info("payan. movafagh: %s | namovafagh: %s", ok, fail)
    logger.info("khoruji: %s", os.path.abspath(args.output_dir))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())