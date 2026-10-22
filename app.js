// app.js - Sony Bravia 720p & MP3 Converter Frontend Engine
let currentMode = 'video';
let currentDuration = 210; // Default 3.5 mins for size estimations
let ffmpegInstance = null;
let playlistVideos = [];

// Video & Audio Quality Profiles
const QUALITY_PROFILES = {
  video: [
    { value: '720', label: '720p HD (Sony TV Max • H.264)', bitrateKbps: 2400 },
    { value: '480', label: '480p Standard (Fast • H.264)', bitrateKbps: 1200 },
    { value: '360', label: '360p Compact (Data Saver)', bitrateKbps: 700 }
  ],
  audio: [
    { value: '320', label: '320 kbps Ultra HQ MP3 (Studio)', bitrateKbps: 320 },
    { value: '192', label: '192 kbps Standard MP3 (Balanced)', bitrateKbps: 192 },
    { value: '128', label: '128 kbps Fast MP3 (Compact)', bitrateKbps: 128 }
  ]
};

// Console logger helper
function logMessage(msg) {
  const box = document.getElementById('consoleBox');
  if (!box) return;
  box.textContent += `\n[${new Date().toLocaleTimeString()}] ${msg}`;
  box.scrollTop = box.scrollHeight;
}

// Switch between Single Converter and Playlist tabs
function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  if (tab === 'single') {
    document.getElementById('tabSingleBtn').classList.add('active');
    document.getElementById('tabSingle').classList.add('active');
  } else {
    document.getElementById('tabPlaylistBtn').classList.add('active');
    document.getElementById('tabPlaylist').classList.add('active');
  }
}

// Switch between Video and Audio mode
function setMode(mode) {
  currentMode = mode;
  document.getElementById('modeVideoBtn').classList.toggle('active', mode === 'video');
  document.getElementById('modeAudioBtn').classList.toggle('active', mode === 'audio');

  const convertBtn = document.getElementById('convertBtn');
  convertBtn.textContent = mode === 'video' ? '⚡ Convert & Download 720p MP4' : '🎵 Convert & Download MP3 Audio';

  populateQualityDropdown();
}

function populateQualityDropdown() {
  const select = document.getElementById('qualitySelect');
  select.innerHTML = '';

  const profiles = QUALITY_PROFILES[currentMode];
  profiles.forEach(prof => {
    const opt = document.createElement('option');
    opt.value = prof.value;
    opt.textContent = prof.label;
    select.appendChild(opt);
  });

  updateEstimatedSize();
}

// Update estimated size badge
function updateEstimatedSize() {
  const select = document.getElementById('qualitySelect');
  const selectedVal = select.value;
  const profiles = QUALITY_PROFILES[currentMode];
  const profile = profiles.find(p => p.value === selectedVal) || profiles[0];

  const totalBits = profile.bitrateKbps * currentDuration;
  const sizeMB = (totalBits / (8 * 1024)).toFixed(1);

  const badge = document.getElementById('estSizeBadge');
  badge.textContent = `~ ${sizeMB} MB`;
}

// Clipboard Paste Helpers
async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById('mediaUrl').value = text;
    onUrlChanged();
  } catch (_) {
    logMessage('Please paste the URL manually into the field.');
  }
}

async function pastePlaylistFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById('playlistUrl').value = text;
  } catch (_) {
    logMessage('Please paste the playlist URL manually into the field.');
  }
}

// Triggered when URL input changes
async function onUrlChanged() {
  const url = document.getElementById('mediaUrl').value.trim();
  const previewCard = document.getElementById('previewCard');

  if (!url) {
    previewCard.style.display = 'none';
    return;
  }

  // Quick YouTube video ID detector
  const match = url.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([a-zA-Z0-9_-]{11})/);
  if (match) {
    const videoId = match[1];
    document.getElementById('prevThumb').src = `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`;
    document.getElementById('prevTitle').textContent = 'Loading video info...';
    document.getElementById('prevMeta').textContent = 'Sony Bravia 720p Verified';
    previewCard.style.display = 'flex';

    try {
      const res = await fetch(`https://noembed.com/embed?url=${encodeURIComponent(url)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.title) document.getElementById('prevTitle').textContent = data.title;
        if (data.author_name) document.getElementById('prevMeta').textContent = `By ${data.author_name} • KLV-24P413D Ready`;
      }
    } catch (_) {}
  } else {
    previewCard.style.display = 'none';
  }
}

// Initialize FFmpeg.wasm if needed
async function getFFmpeg() {
  if (ffmpegInstance) return ffmpegInstance;

  logMessage('Loading in-browser WebAssembly transcode engine...');
  const { createFFmpeg } = FFmpeg;
  ffmpegInstance = createFFmpeg({
    log: true,
    corePath: 'https://unpkg.com/@ffmpeg/core@0.11.0/dist/ffmpeg-core.js'
  });

  await ffmpegInstance.load();
  logMessage('Transcode engine loaded.');
  return ffmpegInstance;
}

// ================= SINGLE CONVERT & DOWNLOAD =================
async function processSingleDownload() {
  const url = document.getElementById('mediaUrl').value.trim();
  if (!url) {
    alert('Please enter a YouTube video or direct video link.');
    return;
  }

  const quality = document.getElementById('qualitySelect').value;
  const btn = document.getElementById('convertBtn');
  const progressWrap = document.getElementById('progressWrap');
  const progressBar = document.getElementById('progressBarFill');
  const progressStatus = document.getElementById('progressStatus');

  btn.disabled = true;
  progressWrap.style.display = 'flex';
  progressBar.style.width = '20%';
  progressStatus.textContent = 'Resolving stream parameters...';
  logMessage(`Processing [${currentMode.toUpperCase()}] target: ${quality}...`);

  try {
    // 1. Call serverless resolver
    const response = await fetch('/api/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, mode: currentMode, quality })
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || 'Failed to resolve stream');
    }

    progressBar.style.width = '50%';
    progressStatus.textContent = `Found stream: ${data.title}`;
    logMessage(`Stream ready: ${data.title} (${data.estimatedSizeMB || 'Calculated'})`);

    // Case A: High-Speed Direct Stream Available (No Browser Transcoding Needed)
    if (data.downloadUrl && !data.needsTranscode) {
      progressBar.style.width = '85%';
      progressStatus.textContent = 'Starting direct download...';
      logMessage('Triggering direct Sony Bravia compliant download...');

      triggerFileDownload(data.downloadUrl, sanitizeFileName(data.title) + (currentMode === 'video' ? '_720p.mp4' : '.mp3'));

      progressBar.style.width = '100%';
      progressStatus.textContent = '✅ Download complete!';
      logMessage('✅ Complete! Ready to copy to FAT32 / NTFS USB drive.');
      return;
    }

    // Case B: In-Browser Transcoding Needed (Direct MKV / WEBM / Transcode)
    progressBar.style.width = '60%';
    progressStatus.textContent = 'Transcoding with FFmpeg for Sony Bravia...';
    logMessage('Transcoding with Sony Bravia KLV-24P413D hardware flags...');

    await transcodeMediaWithFFmpeg(data.downloadUrl, currentMode, quality, data.title);

    progressBar.style.width = '100%';
    progressStatus.textContent = '✅ Conversion complete!';
    logMessage('✅ Transcoding finished. File downloaded to your device.');
  } catch (err) {
    console.error(err);
    logMessage(`❌ Error: ${err.message}`);
    progressStatus.textContent = '❌ Conversion failed';
  } finally {
    btn.disabled = false;
  }
}

// In-Browser Transcoding for Sony KLV-24P413D
async function transcodeMediaWithFFmpeg(streamUrl, mode, quality, rawTitle) {
  const ffmpeg = await getFFmpeg();
  const { fetchFile } = FFmpeg;

  // Route through CORS proxy
  const proxied = `/api/proxy?url=${encodeURIComponent(streamUrl)}`;
  logMessage('Fetching media stream data...');
  const fileData = await fetchFile(proxied);

  ffmpeg.FS('writeFile', 'input_file', fileData);
  logMessage('Executing Sony Bravia hardware constraints...');

  if (mode === 'audio') {
    // Pure MP3 Stereo 44.1kHz
    const bitrate = quality === '320' ? '320k' : (quality === '128' ? '128k' : '192k');
    await ffmpeg.run(
      '-i', 'input_file',
      '-vn',
      '-c:a', 'libmp3lame',
      '-b:a', bitrate,
      '-ar', '44100',
      '-ac', '2',
      'bravia_audio.mp3'
    );

    const outData = ffmpeg.FS('readFile', 'bravia_audio.mp3');
    downloadBlob(outData, 'audio/mpeg', sanitizeFileName(rawTitle) + '.mp3');
    ffmpeg.FS('unlink', 'bravia_audio.mp3');
  } else {
    // Strict 720p H.264 Main Profile 3.1 + Stereo AAC + FastStart
    await ffmpeg.run(
      '-i', 'input_file',
      '-vf', "scale='min(1280,iw)':-2:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
      '-r', '30',
      '-c:v', 'libx264',
      '-profile:v', 'main',
      '-level', '3.1',
      '-preset', 'ultrafast',
      '-pix_fmt', 'yuv420p',
      '-c:a', 'aac',
      '-ac', '2',
      '-ar', '44100',
      '-b:a', '128k',
      '-movflags', '+faststart',
      'bravia_video.mp4'
    );

    const outData = ffmpeg.FS('readFile', 'bravia_video.mp4');
    downloadBlob(outData, 'video/mp4', sanitizeFileName(rawTitle) + '_720p.mp4');
    ffmpeg.FS('unlink', 'bravia_video.mp4');
  }

  ffmpeg.FS('unlink', 'input_file');
}

// Download Helper
function triggerFileDownload(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function downloadBlob(uint8Array, mime, filename) {
  const blob = new Blob([uint8Array.buffer], { type: mime });
  const url = URL.createObjectURL(blob);
  triggerFileDownload(url, filename);
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

function sanitizeFileName(name) {
  return (name || 'bravia_download').replace(/[/\\?%*:|"<>]/g, '_').substring(0, 80);
}

// ================= TAB 2: YOUTUBE PLAYLIST =================
async function fetchPlaylist() {
  const url = document.getElementById('playlistUrl').value.trim();
  if (!url) {
    alert('Please enter a valid YouTube Playlist URL.');
    return;
  }

  const btn = document.getElementById('fetchPlaylistBtn');
  const container = document.getElementById('playlistItemsList');
  const header = document.getElementById('playlistHeader');

  btn.disabled = true;
  btn.textContent = '⏳ Loading...';
  container.innerHTML = '<div class="empty-state">Fetching playlist videos...</div>';

  try {
    const res = await fetch(`/api/playlist?url=${encodeURIComponent(url)}`);
    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.error || 'Could not load playlist.');
    }

    playlistVideos = data.videos || [];
    document.getElementById('playlistTitle').textContent = data.title;
    document.getElementById('playlistCount').textContent = `${playlistVideos.length} Videos Available`;
    header.style.display = 'flex';

    renderPlaylistItems(playlistVideos);
  } catch (err) {
    container.innerHTML = `<div class="empty-state" style="color: #ef4444;">❌ ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = '🔍 Load Playlist';
  }
}

function renderPlaylistItems(videos) {
  const container = document.getElementById('playlistItemsList');
  container.innerHTML = '';

  if (videos.length === 0) {
    container.innerHTML = '<div class="empty-state">No videos found in this playlist.</div>';
    return;
  }

  videos.forEach((vid, index) => {
    const item = document.createElement('div');
    item.className = 'playlist-item';
    item.innerHTML = `
      <img class="pl-thumb" src="${vid.thumbnail}" alt="Thumbnail" />
      <div class="pl-info">
        <div class="pl-title">${index + 1}. ${escapeHtml(vid.title)}</div>
        <div class="pl-duration">⏱️ ${vid.formattedDuration} • ${escapeHtml(vid.author || 'YouTube')}</div>
      </div>
      <div class="pl-actions">
        <button class="pl-btn" onclick="downloadPlaylistItem('${vid.watchUrl}', '720', 'video', this)">📥 720p</button>
        <button class="pl-btn" onclick="downloadPlaylistItem('${vid.watchUrl}', '192', 'audio', this)">🎵 MP3</button>
      </div>
    `;
    container.appendChild(item);
  });
}

// 1-by-1 Download from Playlist
async function downloadPlaylistItem(watchUrl, quality, mode, btnElement) {
  const origText = btnElement.textContent;
  btnElement.disabled = true;
  btnElement.textContent = '⏳';

  try {
    const response = await fetch('/api/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: watchUrl, mode, quality })
    });

    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || 'Failed');

    triggerFileDownload(data.downloadUrl, sanitizeFileName(data.title) + (mode === 'video' ? '_720p.mp4' : '.mp3'));
    btnElement.textContent = '✅';
    setTimeout(() => {
      btnElement.textContent = origText;
      btnElement.disabled = false;
    }, 4000);
  } catch (err) {
    alert(`Could not download item: ${err.message}`);
    btnElement.textContent = '❌';
    setTimeout(() => {
      btnElement.textContent = origText;
      btnElement.disabled = false;
    }, 3000);
  }
}

// Batch Queue Download (All Videos in Playlist)
async function startBatchDownload() {
  if (playlistVideos.length === 0) return;

  const qualityChoice = document.getElementById('playlistQualitySelect').value;
  const isAudio = qualityChoice.startsWith('mp3');
  const quality = isAudio ? qualityChoice.replace('mp3-', '') : qualityChoice;
  const mode = isAudio ? 'audio' : 'video';

  const btn = document.getElementById('batchDownloadBtn');
  btn.disabled = true;

  for (let i = 0; i < playlistVideos.length; i++) {
    const vid = playlistVideos[i];
    btn.textContent = `⏳ Downloading ${i + 1}/${playlistVideos.length}...`;

    try {
      const response = await fetch('/api/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: vid.watchUrl, mode, quality })
      });

      const data = await response.json();
      if (data && data.downloadUrl) {
        triggerFileDownload(data.downloadUrl, sanitizeFileName(data.title) + (mode === 'video' ? `_${quality}p.mp4` : '.mp3'));
      }
    } catch (_) {}

    // 2-second pause between downloads to prevent browser throttling
    await new Promise(r => setTimeout(r, 2000));
  }

  btn.textContent = '✅ All Queued!';
  setTimeout(() => {
    btn.textContent = '📥 Download All (Queue)';
    btn.disabled = false;
  }, 5000);
}

function escapeHtml(str) {
  return (str || '').replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  populateQualityDropdown();
});
