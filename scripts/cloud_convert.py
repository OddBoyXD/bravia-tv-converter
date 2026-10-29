#!/usr/bin/env python3
"""
Cloud Media Converter for Sony Bravia KLV-24P413D (and Universal TVs)
Handles:
1. GoFile links (anti-bot token generation, session cookies, CDN direct URL retrieval)
2. Direct HTTP/HTTPS media streams
3. FFmpeg hardware-constrained transcoding for Sony Bravia TV:
   - Video: H.264 Main Profile Level 3.1, max 1280x720, 30fps, strictly yuv420p
   - Audio: AAC-LC Stereo 192k 44.1kHz or MP3 Stereo 320k 44.1kHz
   - Container: MP4 with +faststart (moov atom at beginning)
4. Uploads to GitHub Release / Cloud storage and outputs 1-click direct download URL
"""

import os
import sys
import re
import time
import json
import hashlib
import argparse
import subprocess
import requests

GOFILE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
GOFILE_LANGUAGE = "en-US"
GOFILE_WT_SALT = os.environ.get("GOFILE_WT_SALT", "12af056dacea0b")
WT_WINDOW_SECONDS = 14400

def generate_gofile_token(account_token: str, window_offset: int = 0) -> str:
    window = int(time.time() // WT_WINDOW_SECONDS) + window_offset
    raw = f"{GOFILE_USER_AGENT}::{GOFILE_LANGUAGE}::{account_token}::{window}::{GOFILE_WT_SALT}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def extract_gofile_id(url: str) -> str:
    match = re.search(r'gofile\.io/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    match = re.search(r'gofile\.io/\?c=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    # Direct content ID or last path segment
    clean = url.strip().split('?')[0].rstrip('/').split('/')[-1]
    return clean

def collect_gofile_files(node):
    files = []
    if not isinstance(node, dict):
        return files
    if node.get("type") == "file" and node.get("link"):
        files.append(node)
    children = node.get("children") or node.get("contents") or {}
    if isinstance(children, dict):
        for child in children.values():
            files.extend(collect_gofile_files(child))
    elif isinstance(children, list):
        for child in children:
            files.extend(collect_gofile_files(child))
    return files

def resolve_gofile_url(gofile_url: str):
    content_id = extract_gofile_id(gofile_url)
    print(f"[*] Resolving GoFile content ID: {content_id}")
    
    session = requests.Session()
    headers = {
        'User-Agent': GOFILE_USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://gofile.io/',
    }
    
    # Step 1: Establish web session
    try:
        session.get(f"https://gofile.io/d/{content_id}", headers=headers, timeout=15)
    except Exception as e:
        print(f"[!] Warning visiting web landing page: {e}")

    # Step 2: Create / fetch guest account token
    account_token = None
    try:
        acc_resp = session.post("https://api.gofile.io/accounts", headers={'User-Agent': GOFILE_USER_AGENT}, timeout=10)
        acc_data = acc_resp.json()
        if acc_data.get("status") == "ok":
            account_token = acc_data.get("data", {}).get("token")
            print(f"[+] Obtained GoFile session token: {account_token[:6]}...")
    except Exception as e:
        print(f"[!] Failed to create guest account: {e}")

    # Step 3: Fetch folder contents
    file_info = None
    for offset in [0, -1, 1]:
        wt = generate_gofile_token(account_token or "", window_offset=offset)
        api_headers = {
            'User-Agent': GOFILE_USER_AGENT,
            'Accept': 'application/json',
            'X-BL': GOFILE_LANGUAGE,
            'X-Website-Token': wt,
            'Referer': f"https://gofile.io/d/{content_id}",
        }
        if account_token:
            api_headers['Authorization'] = f"Bearer {account_token}"
        
        params = {
            'wt': wt,
            'cache': 'true'
        }
        
        try:
            resp = session.get(
                f"https://api.gofile.io/contents/{content_id}",
                headers=api_headers,
                params=params,
                cookies=session.cookies.get_dict(),
                timeout=15
            )
            data = resp.json()
            if data.get("status") == "ok":
                print(f"[debug] GoFile data keys: {list(data.get('data', {}).keys())}")
                print(f"[debug] GoFile full data: {json.dumps(data.get('data', {}))[:1000]}")
                
                d = data.get("data", {})
                files = collect_gofile_files(d)

                if files:
                    # Filter for video/audio or pick the largest file (the movie)
                    files.sort(key=lambda x: x.get("size", 0), reverse=True)
                    file_info = files[0]
                    print(f"[+] Found file in GoFile: {file_info.get('name')} ({file_info.get('size', 0) / (1024*1024):.2f} MB)")
                    break
        except Exception as e:
            print(f"[!] Attempt with offset {offset} failed: {e}")
            
    if not file_info:
        raise RuntimeError("Failed to resolve GoFile link. Content may be expired, private, or password-protected.")
        
    direct_link = file_info.get("link")
    filename = file_info.get("name", f"video_{content_id}.mp4")
    return direct_link, filename, session, account_token

def download_file(url: str, output_path: str, session: requests.Session = None, account_token: str = None):
    print(f"[*] Downloading file from: {url}")
    downloader = session or requests.Session()
    headers = {
        'User-Agent': GOFILE_USER_AGENT,
        'Referer': 'https://gofile.io/'
    }
    if account_token:
        headers['Cookie'] = f"accountToken={account_token}"
    
    with downloader.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        downloaded = 0
        last_log = time.time()
        
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024 * 4): # 4MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if time.time() - last_log > 3:
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            print(f"    -> Download progress: {percent:.1f}% ({mb:.1f} MB / {total_mb:.1f} MB)")
                        else:
                            mb = downloaded / (1024 * 1024)
                            print(f"    -> Downloaded: {mb:.1f} MB")
                        last_log = time.time()
                        
    final_size = os.path.getsize(output_path)
    if final_size == 0:
        raise RuntimeError("Downloaded file is 0 bytes! GoFile may have blocked the direct stream.")
    print(f"[+] Download complete: {output_path} ({final_size / (1024*1024):.2f} MB)")

def transcode_for_bravia(input_path: str, output_path: str, mode: str = "video"):
    print(f"[*] Starting FFmpeg conversion for Sony Bravia (mode={mode})...")
    
    if mode == "video":
        # Target: 720p HD MP4 (H.264 Main 3.1, yuv420p, max 30fps, AAC Stereo 192k 44.1kHz, +faststart)
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", "scale='min(1280,iw)':-2:flags=lanczos",
            "-r", "30",
            "-c:v", "libx264",
            "-profile:v", "main",
            "-level", "3.1",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ac", "2",
            "-ar", "44100",
            "-movflags", "+faststart",
            output_path
        ]
    else:
        # Audio Mode: MP3 320kbps Stereo 44.1kHz
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vn",
            "-c:a", "libmp3lame",
            "-b:a", "320k",
            "-ac", "2",
            "-ar", "44100",
            output_path
        ]
        
    print(f"[*] Executing command: {' '.join(cmd)}")
    start_time = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode != 0:
        print("[!] FFmpeg output error log:")
        print(res.stdout[-1500:])
        raise RuntimeError(f"FFmpeg conversion failed with return code {res.returncode}")
        
    elapsed = time.time() - start_time
    out_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[+] Conversion successful in {elapsed:.1f}s! Output size: {out_size:.2f} MB")

def upload_to_pixeldrain(file_path: str) -> str:
    print(f"[*] Uploading to Pixeldrain: {file_path}")
    filename = os.path.basename(file_path)
    url = f"https://pixeldrain.com/api/file/{filename}"
    with open(file_path, "rb") as f:
        resp = requests.put(url, data=f, timeout=180)
    data = resp.json()
    if data.get("success"):
        file_id = data.get("id")
        direct_url = f"https://pixeldrain.com/api/file/{file_id}?download"
        print(f"[+] Uploaded to Pixeldrain: {direct_url}")
        return direct_url
    raise RuntimeError(f"Pixeldrain upload failed: {resp.text}")

def main():
    parser = argparse.ArgumentParser(description="Convert GoFile / Direct videos for Sony Bravia TV")
    parser.add_argument("--url", required=True, help="GoFile link or direct media URL")
    parser.add_argument("--mode", default="video", choices=["video", "audio"], help="Output mode (video or audio)")
    parser.add_argument("--name", default=None, help="Custom output filename")
    args = parser.parse_args()
    
    input_url = args.url.strip()
    session = None
    
    account_token = None
    if "gofile.io" in input_url:
        direct_url, orig_filename, session, account_token = resolve_gofile_url(input_url)
    else:
        direct_url = input_url
        orig_filename = input_url.split('/')[-1].split('?')[0] or "media_input.mp4"
        
    base_name = os.path.splitext(orig_filename)[0]
    # Clean up name for TV USB
    clean_base = re.sub(r'[^a-zA-Z0-9_\.-]', '_', base_name)[:50]
    
    ext = ".mp4" if args.mode == "video" else ".mp3"
    input_file = f"raw_input_{int(time.time())}{os.path.splitext(orig_filename)[1] or '.mp4'}"
    output_file = f"{args.name or clean_base}_SonyBravia_{'720p' if args.mode == 'video' else 'Audio'}{ext}"
    
    try:
        # Download
        download_file(direct_url, input_file, session, account_token)
        
        # Transcode
        transcode_for_bravia(input_file, output_file, args.mode)
        
        # Set GitHub Action outputs if running inside CI
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"output_file={output_file}\n")
                f.write(f"file_size_mb={os.path.getsize(output_file)/(1024*1024):.2f}\n")
                
        print(f"\n==========================================")
        print(f"🎉 SUCCESS! TV-READY FILE CREATED:")
        print(f"File Name: {output_file}")
        print(f"File Size: {os.path.getsize(output_file)/(1024*1024):.2f} MB")
        print(f"==========================================\n")
        
    finally:
        if os.path.exists(input_file):
            os.remove(input_file)

if __name__ == "__main__":
    main()
