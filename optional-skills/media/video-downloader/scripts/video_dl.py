#!/usr/bin/env python3
"""
video_dl.py — Universal video inspect/download CLI for the Hermes Agent project.

Thin, robust wrapper around yt-dlp (https://github.com/yt-dlp/yt-dlp), which
supports 1000+ sites (YouTube, TikTok, Instagram, X/Twitter, Vimeo, Reddit,
Facebook, Twitch, SoundCloud, etc.). This wrapper adds sane defaults, JSON
output, and a small set of high-level subcommands so an agent can:

  info      print metadata for a link as JSON (title, duration, uploader, ...)
  formats   list available formats/qualities for a link
  download  download a video (quality/section options)
  audio     download audio only (e.g. mp3)
  subs      download subtitles / auto-captions

It shells out to yt-dlp rather than importing it, so it works regardless of how
yt-dlp was installed. Resolution order for the yt-dlp executable:
  1. $YT_DLP_BIN              (explicit path)
  2. `yt-dlp` on PATH
  3. `python3 -m yt_dlp`      (pip-installed module)

Zero non-stdlib imports. ffmpeg is recommended (yt-dlp uses it to merge
video+audio and to extract/convert audio); without it some downloads fall back
to a single pre-muxed format.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import List, Optional


# ---------------------------------------------------------------------------
# yt-dlp resolution
# ---------------------------------------------------------------------------

def _resolve_ytdlp() -> List[str]:
    """Return the argv prefix that invokes yt-dlp, or exit with guidance."""
    env_bin = os.environ.get("YT_DLP_BIN")
    if env_bin:
        return [env_bin]
    on_path = shutil.which("yt-dlp")
    if on_path:
        return [on_path]
    # Fall back to the module if it is importable under the current interpreter.
    try:
        subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            check=True,
            capture_output=True,
        )
        return [sys.executable, "-m", "yt_dlp"]
    except Exception:
        sys.stderr.write(
            "ERROR: yt-dlp not found.\n"
            "Install it in an isolated environment (PEP 668-safe):\n"
            "  python3 -m venv /tmp/video-dl-venv\n"
            "  /tmp/video-dl-venv/bin/pip install -U yt-dlp\n"
            "  export YT_DLP_BIN=/tmp/video-dl-venv/bin/yt-dlp\n"
            "Also install ffmpeg for best-quality merges (apt/brew install ffmpeg).\n"
        )
        sys.exit(2)


def _run(argv: List[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(argv, check=True, text=True,
                          capture_output=capture)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_info(yt: List[str], args) -> int:
    """Dump per-video metadata as JSON (one object per video; playlists stream)."""
    argv = yt + ["-J", "--no-warnings"]
    if args.no_playlist:
        argv.append("--no-playlist")
    argv.append(args.url)
    proc = _run(argv, capture=True)
    data = json.loads(proc.stdout)
    # Project the most useful fields; keep raw under "_raw" off by default.
    def slim(e: dict) -> dict:
        return {
            "id": e.get("id"),
            "title": e.get("title"),
            "uploader": e.get("uploader") or e.get("channel"),
            "duration": e.get("duration"),
            "duration_string": e.get("duration_string"),
            "view_count": e.get("view_count"),
            "like_count": e.get("like_count"),
            "upload_date": e.get("upload_date"),
            "webpage_url": e.get("webpage_url"),
            "extractor": e.get("extractor"),
            "is_live": e.get("is_live"),
            "description": (e.get("description") or "")[:500],
        }
    if data.get("_type") == "playlist":
        out = {
            "type": "playlist",
            "title": data.get("title"),
            "count": data.get("playlist_count") or len(data.get("entries") or []),
            "entries": [slim(e) for e in (data.get("entries") or []) if e],
        }
    else:
        out = slim(data)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_formats(yt: List[str], args) -> int:
    """List available formats/qualities (human table from yt-dlp)."""
    argv = yt + ["-F", "--no-warnings"]
    if args.no_playlist:
        argv.append("--no-playlist")
    argv.append(args.url)
    _run(argv)
    return 0


def cmd_download(yt: List[str], args) -> int:
    """Download video. Default = best quality merged to mp4 when possible."""
    os.makedirs(args.out, exist_ok=True)
    argv = yt + ["--no-warnings", "-P", args.out]
    if args.no_playlist:
        argv.append("--no-playlist")
    if args.format:
        argv += ["-f", args.format]
    else:
        # Best video+audio, cap height if requested, prefer mp4 container.
        height = f"[height<={args.max_height}]" if args.max_height else ""
        argv += ["-f", f"bv*{height}+ba/b{height}",
                 "--merge-output-format", "mp4"]
    if args.section:
        # e.g. "*00:01:00-00:02:00" — needs ffmpeg.
        argv += ["--download-sections", args.section, "--force-keyframes-at-cuts"]
    if args.template:
        argv += ["-o", args.template]
    argv.append(args.url)
    _run(argv)
    return 0


def cmd_audio(yt: List[str], args) -> int:
    """Download audio only and convert (default mp3). Needs ffmpeg."""
    os.makedirs(args.out, exist_ok=True)
    argv = yt + ["--no-warnings", "-P", args.out,
                 "-x", "--audio-format", args.codec, "--audio-quality", "0"]
    if args.no_playlist:
        argv.append("--no-playlist")
    if args.template:
        argv += ["-o", args.template]
    argv.append(args.url)
    _run(argv)
    return 0


def cmd_subs(yt: List[str], args) -> int:
    """Download subtitles / auto-captions without the video."""
    os.makedirs(args.out, exist_ok=True)
    argv = yt + ["--no-warnings", "-P", args.out, "--skip-download",
                 "--write-subs", "--sub-langs", args.langs, "--convert-subs", "srt"]
    if args.auto:
        argv.append("--write-auto-subs")
    if args.no_playlist:
        argv.append("--no-playlist")
    argv.append(args.url)
    _run(argv)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="video_dl.py",
        description="Inspect and download videos from 1000+ sites via yt-dlp.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp):
        sp.add_argument("url", help="Video or playlist URL.")
        sp.add_argument("--no-playlist", action="store_true",
                        help="If URL is part of a playlist, grab only the single video.")

    sp = sub.add_parser("info", help="Print metadata as JSON.")
    add_common(sp)

    sp = sub.add_parser("formats", help="List available formats/qualities.")
    add_common(sp)

    sp = sub.add_parser("download", help="Download a video.")
    add_common(sp)
    sp.add_argument("-o", "--out", default="./downloads", help="Output directory.")
    sp.add_argument("-f", "--format", help="Explicit yt-dlp format selector (overrides --max-height).")
    sp.add_argument("--max-height", type=int, help="Cap resolution, e.g. 1080.")
    sp.add_argument("--section", help='Download a clip, e.g. "*00:01:00-00:02:00".')
    sp.add_argument("--template", help="yt-dlp output template, e.g. '%%(title)s.%%(ext)s'.")

    sp = sub.add_parser("audio", help="Download audio only.")
    add_common(sp)
    sp.add_argument("-o", "--out", default="./downloads", help="Output directory.")
    sp.add_argument("--codec", default="mp3", help="Audio codec/format (mp3, m4a, opus, ...).")
    sp.add_argument("--template", help="yt-dlp output template.")

    sp = sub.add_parser("subs", help="Download subtitles / captions.")
    add_common(sp)
    sp.add_argument("-o", "--out", default="./downloads", help="Output directory.")
    sp.add_argument("--langs", default="en", help="Comma-separated sub languages, e.g. 'en,es'.")
    sp.add_argument("--auto", action="store_true", help="Include auto-generated captions.")

    return p


DISPATCH = {
    "info": cmd_info,
    "formats": cmd_formats,
    "download": cmd_download,
    "audio": cmd_audio,
    "subs": cmd_subs,
}


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    yt = _resolve_ytdlp()
    try:
        return DISPATCH[args.cmd](yt, args)
    except subprocess.CalledProcessError as e:
        if e.stderr:
            sys.stderr.write(e.stderr)
        sys.stderr.write(f"\nyt-dlp exited with status {e.returncode}\n")
        return e.returncode or 1
    except json.JSONDecodeError:
        sys.stderr.write("ERROR: could not parse yt-dlp JSON output.\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
