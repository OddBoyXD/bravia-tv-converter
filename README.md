# 📺 Sony Bravia 720p & MP3 Converter

A 100% free, 24/7 web application designed to convert, downscale, and download any video, audio stream, YouTube link, or YouTube playlist specifically formatted for the **Sony Bravia KLV-24P413D** (Non-Smart LED TV) and older USB media players.

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
1. **Single Video & Audio Converter**:
   - Accepts YouTube links, Shorts, or direct video streams (MKV, MOV, FLV, WEBM, MP4, etc.).
   - Video Qualities: **720p HD (Sony TV Max)**, **480p Standard**, **360p Compact**.
   - Audio Qualities: **320 kbps (Ultra HQ MP3)**, **192 kbps (Standard MP3)**, **128 kbps (Fast MP3)**.
2. **Live Dynamic File Size Estimator**:
   - Calculates estimated file size before downloading.
3. **Dedicated YouTube Playlist Tab**:
   - Paste any YouTube playlist URL.
   - View titles, thumbnails, and durations.
   - **Download 1-by-1**: Dedicated 720p and MP3 buttons for each individual video.
   - **Download All (Queue)**: Automatically batches and downloads the entire playlist.
4. **Hybrid Transcoding**:
   - Instant high-speed direct downloads for supported streams.
   - In-browser **FFmpeg.wasm** engine for direct MKV/WEBM transcoding with zero server costs.
5. **Mobile-First Responsive Interface**:
   - Fast, tactile dark-mode interface optimized for mobile and desktop.

---

## 🚀 100% Free 24/7 Deployment (Vercel)

1. Fork or import this repository into your GitHub account.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Select this repository (`bravia-tv-converter`) and click **"Deploy"**.
4. In under 30 seconds, your site will be live 24/7 at `https://your-project.vercel.app`!
