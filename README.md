# yt-downloader

A small tool I built to download a lot of YouTube videos at once — single videos or whole
playlists — together with their subtitles, and keep track of what's already done.

I usually run it on a headless Ubuntu box over SSH, but there's a Windows path too (see below).

## What it does

You give it a text file with links. On each run it:

- downloads every video at 1080p, or the best quality available if 1080 isn't there, always with audio
- pulls English subtitles (the real ones if they exist, otherwise the auto-generated ones) as `.srt`
- breaks playlists down into individual video links and writes them back into the list
- deletes the links that finished successfully, so a second run only retries the failures

That last part is really the point of the whole thing. The link file turns into a to-do list that
cleans itself up as it goes. If a download dies halfway (bad connection, a video that errors out,
whatever), you just run it again and it picks up where it left off.

## Why not just call yt-dlp by hand?

You can, and that's basically all this does under the hood. But I kept running into the same stuff:

- YouTube decides your datacenter IP is a bot and refuses to serve anything
- playlists are a pain to track when some videos fail and some don't
- re-running a long list meant skimming progress output to figure out what was already downloaded

So this wraps yt-dlp with the right flags, adds cookies handling, retries, subtitles, a log, and
that self-cleaning link list. Nothing fancy.

## Requirements

- Python 3.10+
- `yt-dlp`
- `ffmpeg` (needed to merge video + audio and to convert subtitles)
- `deno` (YouTube needs a JS engine these days for part of the extraction; optional but recommended)

The setup scripts install all of it.

## Install

### Ubuntu (or any Debian-ish server)

```bash
cd yt-downloader
chmod +x setup.sh
./setup.sh
```

That installs ffmpeg, creates a venv, installs yt-dlp, and puts deno in `~/.deno/bin`.

### Windows

Run `setup_windows.ps1` (right-click → Run with PowerShell, or the `-ExecutionPolicy Bypass` form).
Then `download_windows.bat` to run it.

## Usage

Put your links in `videos.txt`, one per line. Both of these work:

```
https://www.youtube.com/watch?v=SOME_ID
https://www.youtube.com/playlist?list=PL_SOMETHING
```

Then:

```bash
./download.sh
```

A few options I actually use:

```bash
./download.sh --quality 720
./download.sh --no-expand          # don't split playlists into single links
./download.sh --no-remove-links    # keep finished links in the file
```

Files land in `downloads/<title>/`, with the `.mp4` and the `.srt` side by side.

## Cookies (the annoying part)

If you run this from a VPS, YouTube will very likely throw `Sign in to confirm you're not a bot`.
The fix that works is cookies from a logged-in account:

```bash
# grab cookies from a browser into a file (do this on your own machine)
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download <some_url>
# then drop cookies.txt next to the script
```

On Windows you can skip the file entirely and read straight from the browser:

```powershell
.\.venv\Scripts\python.exe yt_download.py --cookies-from-browser chrome
```

Heads up: use a throwaway Google account for this. Logging a datacenter IP into your main account
is asking for trouble. Cookies also expire after a while, so you'll need to refresh them now and then.

## Running it in the background

Downloads can take a while, so run them inside tmux:

```bash
tmux new -s ytdl
./download.sh
# detach with Ctrl+b then d, reattach with tmux attach -t ytdl
```

## Files

```
yt-downloader/
├── yt_download.py         # the actual program
├── download.sh            # Linux wrapper
├── setup.sh               # Linux setup
├── setup_windows.ps1      # Windows setup
├── download_windows.bat   # Windows wrapper
├── videos.txt             # your links
├── archive.txt            # yt-dlp's record of what's been downloaded (auto)
├── cookies.txt            # optional, for the bot check
├── downloads/             # output
└── logs/
```

## Notes

- Subtitle language is configurable with `--subs-langs` (default `en.*`).
- Quality selection is `bv*[height<=N]+ba/b[height<=N]/bv*+ba/b`, so worst case it still gets you
  the best video that has audio.
- It sends subtitles as separate `.srt` files, not embedded in the video.
