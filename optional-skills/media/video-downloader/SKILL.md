---
name: video-downloader
description: "Inspect and download videos/audio from 1000+ sites by link (yt-dlp)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, download, yt-dlp, youtube, tiktok, instagram, twitter, x, vimeo, reddit, twitch, audio, mp3, subtitles, captions, media]
    category: media
    related_skills: [youtube-content]
    requires_toolsets: [terminal]
---

# Video Downloader Skill

Inspect and download video or audio from a link across 1000+ sites using
[yt-dlp](https://github.com/yt-dlp/yt-dlp): YouTube, TikTok, Instagram, X/Twitter,
Vimeo, Reddit, Facebook, Twitch, SoundCloud, and many more.

A thin wrapper script (`video_dl.py`) adds sane defaults and JSON output over
yt-dlp with five subcommands: `info`, `formats`, `download`, `audio`, `subs`.

> For YouTube **transcript-to-text/summary** workflows (no media files), use the
> `youtube-content` skill instead. This skill is about pulling the actual media.

---

## When to Use
- User shares a video link and wants to **download** it (any site yt-dlp supports)
- User wants the **metadata** of a link (title, duration, uploader, views) as JSON
- User wants to **list available qualities/formats** before downloading
- User wants **audio only** (e.g. extract an mp3 from a video)
- User wants **subtitles or auto-captions** as `.srt`
- User wants to grab a **clip / time section** of a longer video

---

## Prerequisites
Python 3.8+ standard library only for the wrapper. The engine is **yt-dlp**, plus
**ffmpeg** (recommended — yt-dlp uses it to merge best video+audio and to
extract/convert audio). Many Linux distros enforce PEP 668, so install yt-dlp in
an isolated environment:

```bash
python3 -m venv /tmp/video-dl-venv
/tmp/video-dl-venv/bin/pip install -U yt-dlp
export YT_DLP_BIN=/tmp/video-dl-venv/bin/yt-dlp   # wrapper picks this up
# ffmpeg (best-quality merges + audio conversion):
#   Debian/Ubuntu: sudo apt install ffmpeg   |   macOS: brew install ffmpeg
```

The wrapper resolves yt-dlp in this order: `$YT_DLP_BIN` → `yt-dlp` on PATH →
`python3 -m yt_dlp`. Keep yt-dlp updated (`pip install -U yt-dlp`) — sites change
their players often and stale versions break.

Helper script path: `~/.hermes/skills/media/video-downloader/scripts/video_dl.py`

---

## Quick Reference

```
SCRIPT=~/.hermes/skills/media/video-downloader/scripts/video_dl.py

# Inspect
python3 $SCRIPT info     "URL"                       # metadata as JSON
python3 $SCRIPT info     "URL" --no-playlist          # single video from a playlist URL
python3 $SCRIPT formats  "URL"                        # list qualities/formats

# Download video
python3 $SCRIPT download "URL"                        # best quality -> ./downloads
python3 $SCRIPT download "URL" -o /path/out           # custom output dir
python3 $SCRIPT download "URL" --max-height 1080      # cap resolution
python3 $SCRIPT download "URL" -f 137+140             # explicit format selector
python3 $SCRIPT download "URL" --section "*00:01:00-00:02:00"   # clip (needs ffmpeg)

# Audio only (needs ffmpeg)
python3 $SCRIPT audio    "URL"                        # -> mp3
python3 $SCRIPT audio    "URL" --codec m4a

# Subtitles / captions
python3 $SCRIPT subs     "URL" --langs en,es          # human subs as .srt
python3 $SCRIPT subs     "URL" --auto                 # include auto-generated captions
```

---

## Procedure

### 0. Setup Check
```bash
python3 --version            # 3.8+
yt-dlp --version || /tmp/video-dl-venv/bin/yt-dlp --version
ffmpeg -version | head -1    # optional but recommended
```

### 1. Inspect Before Downloading
Always confirm what the link is before pulling bytes.
```bash
python3 $SCRIPT info "https://www.youtube.com/watch?v=VIDEO_ID"
```
Returns JSON (title, uploader, duration, view_count, upload_date, webpage_url,
truncated description). Playlist URLs return a `type: playlist` summary with an
`entries` list.

### 2. Pick a Quality (optional)
```bash
python3 $SCRIPT formats "URL"
```
Then either pass `--max-height 1080` for a simple cap, or `-f <selector>` for an
exact yt-dlp format selector (e.g. `bv*[height<=720]+ba`).

### 3. Download
```bash
python3 $SCRIPT download "URL" -o ./downloads --max-height 1080
```
Default selector is `bv*+ba/b` merged to `mp4`. Without ffmpeg, yt-dlp falls back
to the best single pre-muxed stream.

### 4. Audio Only
```bash
python3 $SCRIPT audio "URL" --codec mp3 -o ./downloads
```

### 5. Subtitles
```bash
python3 $SCRIPT subs "URL" --langs en --auto -o ./downloads
```

### 6. Clip a Section
```bash
python3 $SCRIPT download "URL" --section "*00:01:30-00:02:45"
```

---

## Pitfalls
- **Stale yt-dlp breaks sites.** If a download suddenly fails, `pip install -U yt-dlp` first.
- **ffmpeg matters.** Best-quality YouTube downloads are separate video+audio streams; without ffmpeg they cannot be merged and `audio`/`--section` won't work.
- **Auth-gated content.** Private/age-restricted/member-only videos need cookies. Pass them via yt-dlp's `--cookies`/`--cookies-from-browser` (not exposed by this wrapper — call yt-dlp directly for those, or set `YT_DLP_BIN` and add flags).
- **Rate limits / bot checks.** Sites like YouTube and Instagram may throttle or challenge. Retry later; avoid bulk scraping.
- **Playlists.** A watch URL that carries a `&list=` param downloads the whole playlist unless you pass `--no-playlist`.
- **Legal/ToS.** Only download content you have the right to. Respect each platform's Terms of Service and applicable copyright law. This tool is for legitimate use (your own content, licensed media, archival, research).
- **Live streams.** `is_live` content downloads as an ongoing capture until stopped; expect large files.

---

## Verification
```bash
SCRIPT=~/.hermes/skills/media/video-downloader/scripts/video_dl.py
# Metadata only — should print JSON with a title, no files written:
python3 $SCRIPT info "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-playlist
# Formats table — should list available qualities:
python3 $SCRIPT formats "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
