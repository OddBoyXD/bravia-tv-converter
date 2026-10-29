# 📺 Sony Bravia 720p & MP3 Converter

A 100% free, 24/7 web application designed to convert, downscale, and download any direct video URL, audio stream, local phone storage file, YouTube link, or playlist specifically formatted for the **Sony Bravia KLV-24P413D** (Non-Smart LED TV) and older USB media players.

---

## 🎯 Target Hardware Specifications (Sony Bravia KLV-24P413D)
* **Native Panel Resolution**: 1366x768 (720p HD Ready)
* **Maximum Video Input**: **1280x720 @ 30fps** (Higher resolutions like 1080p, 2K, or 4K show *"Playback not available"* on the TV).
* **Video Codec**: **H.264 (MPEG-4 AVC) Main Profile Level 3.1**, strictly **`yuv420p`** color format.
* **Audio Codec**: **MP3** (MPEG-1 Audio Layer III) and **AAC-LC** (2-channel Stereo @ 44.1kHz).
* **Container**: **MP4** with **FastStart** (`moov` atom at file beginning).
* **USB Format**: Strictly **FAT32** or **NTFS**.

---

## ✨ Features
1. **⚡ GoFile & 24/7 Cloud TV Transcoder (Zero Phone Load)**:
   - Paste any **GoFile URL** (e.g. `https://gofile.io/d/YvXabCy1`) or heavy movie link.
   - Bypasses GoFile anti-scraping checks dynamically and downloads at 500+ Mbps directly in the cloud.
   - Runs full hardware-constrained FFmpeg transcoding inside **GitHub Actions (4 vCPUs, 16GB RAM, 100GB SSD)**.
   - Generates permanent, unlimited bandwidth 1-click download links via GitHub Releases.
   - Zero phone battery drain, zero mobile data wasted on raw file transcoding.
2. **Direct Video & Audio URL Conversion**:
   - Accepts direct links to `.mp4`, `.mkv`, `.webm`, `.avi`, `.mov`, `.flv`, `.ts`, `.mp3`, `.m4a`, `.wav`, etc.
   - Client-side streaming download with live percentage indicator and multi-mirror CORS bypass.
   - Converts directly in-browser using FFmpeg.wasm with exact Sony Bravia KLV-24P413D hardware constraints.
2. **📁 Local Phone Storage File Conversion (Zero Data Consumption)**:
   - Select any video or audio file directly from your phone's storage.
   - Transcodes locally on device via WebAssembly at high speed with 0 KB mobile data usage!
3. **YouTube Links & Companion Cookie Support**:
   - Resolves YouTube videos and Shorts into compliant formats.
   - Bypasses YouTube's *"Sign in to confirm you're not a bot"* using Netscape cookies exported with the companion **YT Cookie Exporter** app (`OddBoyXD/yt-cookie-exporter`).
   - Integrated 1-tap Fast Mirrors: Cobalt Web, Y2Mate, and SaveFrom.
4. **Live Dynamic File Size Estimator**:
   - Calculates estimated file size dynamically before downloading based on video duration and profile bitrate.
5. **Dedicated YouTube Playlist Tab**:
   - Paste any YouTube playlist URL to load all videos with titles, thumbnails, and durations.
   - Convert individually (720p MP4 / MP3) or batch download the whole playlist sequentially.
6. **Universal Browser Compatibility**:
   - Automatically uses multi-threaded WebAssembly if `crossOriginIsolated` is supported, or falls back to single-threaded WebAssembly (`core-st`) so it runs flawlessly on any mobile browser without crashing.

---

## 🚀 Live Access
* **GitHub Pages (Static Host)**: [https://oddboyxd.github.io/bravia-tv-converter/](https://oddboyxd.github.io/bravia-tv-converter/)
* **Vercel (Full Serverless Support)**: Deploy with 1 click on [Vercel](https://vercel.com) by importing `OddBoyXD/bravia-tv-converter`.
