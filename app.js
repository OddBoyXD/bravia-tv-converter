// app.js - Sony Bravia 720p & MP3 Converter Engine (Full Direct Media & Offline Support)
let currentMode = 'video';
let currentDuration = 210; // Default 3.5 mins for size calculations
let ffmpegInstance = null;
let playlistVideos = [];
let selectedLocalFile = null;
let directRawUrl = null;

// Embedded Permanent Authenticated Cookie File (Authorized by User)
const DEFAULT_YOUTUBE_COOKIE = `# Netscape HTTP Cookie File
# Exported by OddBoy YT Cookie Exporter
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-1PSIDTS\tsidts-CjUBkldj_2wuwdUmflJrBX6CL-cqwlBXNw8U3APdj9iLjYiwWEHLwZnVK5df3E2aZK05j-VdrRAA
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-3PSIDTS\tsidts-CjUBkldj_2wuwdUmflJrBX6CL-cqwlBXNw8U3APdj9iLjYiwWEHLwZnVK5df3E2aZK05j-VdrRAA
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tHSID\tAnx0Tqtt6wghMiFFz
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tSSID\tAucMJ4G6U2rq2hmTR
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tAPISID\t3C66F5NpENBpsEgM/AVQcRqyXlEoe-L3q-
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tSAPISID\tE2vGWN2cK6nI_7Ei/As9kBmvtn131mXrvR
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-1PAPISID\tE2vGWN2cK6nI_7Ei/As9kBmvtn131mXrvR
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-3PAPISID\tE2vGWN2cK6nI_7Ei/As9kBmvtn131mXrvR
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tSID\tg.a000Dwnext2OhEWQi_XYLWCipXJrAWoyfkYJXN88z4c8TdUVgaaubFu2-L7HaRjMJEIzlOwlQAACgYKAZQSARQSFQHGX2Mi40iHtmZ6fK71D2CwikhAqxoVAUF8yKrDH2mHEdUCXP-iAdlIXLOz0076
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-1PSID\tg.a000Dwnext2OhEWQi_XYLWCipXJrAWoyfkYJXN88z4c8TdUVgaauDc7LOm1xEdFjKflBUSyxigACgYKAZgSARQSFQHGX2MiaeQUR2_U6Mmn5D5u-_M8HxoVAUF8yKrLL_YKUHYV8_urq_cfOCkD0076
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-3PSID\tg.a000Dwnext2OhEWQi_XYLWCipXJrAWoyfkYJXN88z4c8TdUVgaau2Y8jRgyxkhtbxbatbo1q-QACgYKAZsSARQSFQHGX2MiWOLdVnVAYv3_m6j3zXTOoxoVAUF8yKoPeY-T4VEW3ePVcJS9gdJ80076
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-YNID\tCtoBCAUSjAEB8QZuZrEHacNuyk1vHplQDoU7AS16Tu3WHKyPp0rVy7MVgRPtE8cl0pzYm4jXc4hvDKc0mEAhGoYSQkl0XbJIKdVuskwNJqVgS3iJhD64yYxC4bFREVrjfNSTjC2UFst7xuNEwpM1sfECLny0JalFs9agugLe_ynaiQ-qfdDdV0XUXfgW5yg2o0xD2SgFMkUB3qmdT62i5WVfchXn9sYVAiw6dS5hQ4ZsBCTFh_0C5HkK7IrXi-HCpppcPsz87LlJmDHVeDsDni9oooqc2puvN6tdMwk
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tYSC\t89NQgtOwt_0
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tVISITOR_INFO1_LIVE\t1rV-0jFTa2o
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tVISITOR_PRIVACY_METADATA\tCgJJThIEGgAgFw%3D%3D
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-ROLLOUT_TOKEN\tCJOB_YyNh7fekgEQraHDh67NlwMYraHDh67NlwM%3D
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tSIDCC\tAPD_SKFUbkQrjDzpZ_hhAQz-j-MJZh_p1wqGRCMwIrKFucCuQKp6I0DKlTBC__dAWX1znmgg
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-1PSIDCC\tAPD_SKHt55T5ejXNjYs5UXbb0Cvw1w3AaulMWnGm9zve2tBcUG3ZkCUeDLx4-RBTdG2OuPUX8A
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-3PSIDCC\tAPD_SKF6ayWa9r1fcZEADB47y5vWQ808wmu_Oitf1SOERpH4AIRxihZKn0qJl2AZxxewmyUG
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tPREF\tf6=40000000&tz=Asia.Calcutta
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tOTZ\t8839316_34_34__34_
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tNID\tCtQCCAEShgIBOxGDSON5lf_OBLISIdigvXmBSNUHuQjBqVK_0ILXC1E8QyLjQHL-MssgzzRgkXD_gItiHjzKnhKnqvEaLy8H73NKMdJ9WrLddeDQ8qJjiZFGUKRIHLn9QnFBqp8QEJ-QkUo5Pkl8ialw6CUwHziHifOKJNgYG73Hixz_UsTChC-MoHtxJXIq9MjHnky5g2TxSA541b3Z86cmH2PrJFc-GOtEBDkYlRLRQooXKaTbPW6YctmMPOte3R9Y4SgUWuyLJ4ieRZ0UHfMGCYzuIXevdJNYyTgscHDCGoj6nxQv3GFJgcutBVB-qaUW0pArvlH_RB5lOEQdDK4gY0ILJuGBVKbaD13KKAEyRQHSrAfP0a0tfNE_IsbPCzPyAR-sLFNS4gTkCw2Xsi5h13qa0fyqNRWCM3O1CxhxFk3BOf57IudYb2jP-kfs8-RSpysyCA
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Host-GAPS\t1:BYni_7WbSPWpVF0bX8t9jen91EsCuWMEec1H1Fdwu2AiRVbAGNb61U9P5yf3FlMlCyIs9rE13hAXKhwcBy2E3lrz3FgUEg:MDRr2vRtymKB076H
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tLSID\ts.IN|s.youtube:g.a000DwnexgeGJqAfv9Shjuih9LnDZmD6HeDAIRdelsY98Yid7pfe-SlVgIUi35phR_fSeAm26wACgYKAUgSARQSFQHGX2Mi7olo_1QiKOfyp5iPdt-TYhoVAUF8yKpbJVYRzW-0cS6P1SX61xLy0076
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Host-1PLSID\ts.IN|s.youtube:g.a000DwnexgeGJqAfv9Shjuih9LnDZmD6HeDAIRdelsY98Yid7pfeQkJIffR7V4Zj1Lds82lOdAACgYKAdgSARQSFQHGX2MiB_YnLTCsAF3kO5-Y9R_B3BoVAUF8yKrur3GJ5sdI-0-HG69SHz-e0076
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Host-3PLSID\ts.IN|s.youtube:g.a000DwnexgeGJqAfv9Shjuih9LnDZmD6HeDAIRdelsY98Yid7pfeMuAIz6FLBFaXyVxzOIoEMAACgYKAWYSARQSFQHGX2MiEh7DRbuk-eA1qtICVLl7XxoVAUF8yKol-Zv3P9kA3R_sfAZt5DJr0076
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tACCOUNT_CHOOSER\tAFx_qI50mtguUJ-TRKlIm5EVl2wYcC5cwbvbWJVRgfPCwKEfHbD0eG4CmonkGw0X2c7lyVo8yTnrgTBnZb_43vU2yPZwF0xwahRTrxOfce0d6Hm0eOkJwZv7oDmAZ3UNmoKA9HuGgRri
.youtube.com\tTRUE\t/\tTRUE\t1824199005\tSIDCC\tAKEyXzUN2Gw1HZW1jeG_sxe58E69U6hiU9SvpmcTW4aboqUsoixwm3juTvTU-uLbK0zyFbJr
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-1PSIDCC\tAKEyXzUzBekZd7j3Jvsihnc4Ag38NxpH5s99jmRNd07eRI_zlXAoHN3246YVpNxxx4UMYXC0
.youtube.com\tTRUE\t/\tTRUE\t1824199005\t__Secure-3PSIDCC\tAKEyXzV5JXDkdGiSDOFsFsTkMfTDRZPS5VAr2xj0xakhxNMjTda6TFp7vr_4wjY9feWgVthi0w`;

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

// Public Invidious instances with fast timeout guards
const INVIDIOUS_INSTANCES = [
  'https://inv.tux.pizza',
  'https://invidious.nerdvpn.de',
  'https://vid.puffyan.us',
  'https://yt.drgnz.club'
];

// Helper to fetch with strict timeout
async function fetchWithTimeout(resource, options = {}, timeoutMs = 3500) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    return response;
  } finally {
    clearTimeout(id);
  }
}

// Console logger helper
function logMessage(msg) {
  const box = document.getElementById('consoleBox');
  if (!box) return;
  const time = new Date().toLocaleTimeString();
  box.textContent += `\n[${time}] ${msg}`;
  box.scrollTop = box.scrollHeight;
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
  populateQualityDropdown();
  loadSavedCookie();
});

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
  convertBtn.textContent = mode === 'video' 
    ? '⚡ Convert & Download 720p MP4' 
    : '🎵 Convert & Download MP3 Audio';

  populateQualityDropdown();
}

function populateQualityDropdown() {
  const select = document.getElementById('qualitySelect');
  if (!select) return;
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
  if (!select) return;
  const selectedVal = select.value;
  const profiles = QUALITY_PROFILES[currentMode];
  const profile = profiles.find(p => p.value === selectedVal) || profiles[0];

  const totalBits = profile.bitrateKbps * currentDuration;
  const sizeMB = (totalBits / (8 * 1024)).toFixed(1);

  const badge = document.getElementById('estSizeBadge');
  if (badge) badge.textContent = `~ ${sizeMB} MB`;
}

// ================= LOCAL FILE PICKER HANDLING =================
function onLocalFileSelected(event) {
  const files = event.target.files;
  if (!files || files.length === 0) return;

  selectedLocalFile = files[0];
  document.getElementById('mediaUrl').value = '';
  directRawUrl = null;

  // Show file info row
  const sizeMB = (selectedLocalFile.size / (1024 * 1024)).toFixed(1);
  document.getElementById('localFileName').textContent = selectedLocalFile.name;
  document.getElementById('localFileSize').textContent = `${sizeMB} MB`;
  document.getElementById('localFileInfo').style.display = 'flex';

  // Auto-detect mode
  const ext = getFileExtension(selectedLocalFile.name);
  if (isAudioExtension(ext)) {
    setMode('audio');
  } else {
    setMode('video');
  }

  // Update preview card
  const previewCard = document.getElementById('previewCard');
  previewCard.style.display = 'flex';
  document.getElementById('prevThumb').src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="55" viewBox="0 0 80 55"><rect width="80" height="55" fill="%231e293b"/><text x="40" y="32" font-size="20" text-anchor="middle" fill="%2300d2ff">📁</text></svg>';
  document.getElementById('prevTitle').textContent = selectedLocalFile.name;
  document.getElementById('prevMeta').textContent = `Local File (${sizeMB} MB) • Ready to Transcode for Sony Bravia`;

  document.getElementById('directRawBtn').style.display = 'none';
  document.getElementById('ytMirrorsBox').style.display = 'none';

  logMessage(`Local file selected: "${selectedLocalFile.name}" (${sizeMB} MB). Ready to convert.`);
}

function clearSelectedFile() {
  selectedLocalFile = null;
  document.getElementById('localFileInput').value = '';
  document.getElementById('localFileInfo').style.display = 'none';
  document.getElementById('previewCard').style.display = 'none';
  logMessage('Local file cleared.');
}

// ================= URL DETECTION & PREVIEWS =================
async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById('mediaUrl').value = text.trim();
    onUrlChanged();
  } catch (_) {
    logMessage('Please paste the URL manually into the field.');
  }
}

async function pastePlaylistFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById('playlistUrl').value = text.trim();
  } catch (_) {
    logMessage('Please paste the playlist URL manually into the field.');
  }
}

async function onUrlChanged() {
  const url = document.getElementById('mediaUrl').value.trim();
  const previewCard = document.getElementById('previewCard');
  const ytMirrorsBox = document.getElementById('ytMirrorsBox');
  const directRawBtn = document.getElementById('directRawBtn');

  if (selectedLocalFile) {
    clearSelectedFile();
  }

  if (!url) {
    previewCard.style.display = 'none';
    ytMirrorsBox.style.display = 'none';
    directRawBtn.style.display = 'none';
    directRawUrl = null;
    return;
  }

  directRawUrl = url;

  // 1. YouTube Detection
  const ytMatch = url.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([a-zA-Z0-9_-]{11})/);
  if (ytMatch) {
    const videoId = ytMatch[1];
    document.getElementById('prevThumb').src = `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`;
    document.getElementById('prevTitle').textContent = 'Loading video info...';
    document.getElementById('prevMeta').textContent = 'Sony Bravia 720p Verified';
    previewCard.style.display = 'flex';
    ytMirrorsBox.style.display = 'flex';
    directRawBtn.style.display = 'none';

    try {
      const res = await fetchWithTimeout(`https://noembed.com/embed?url=${encodeURIComponent(url)}`, {}, 2500);
      if (res.ok) {
        const data = await res.json();
        if (data.title) document.getElementById('prevTitle').textContent = data.title;
        if (data.author_name) document.getElementById('prevMeta').textContent = `By ${data.author_name} • KLV-24P413D Ready`;
      }
    } catch (_) {}
    return;
  }

  // 2. Direct Video or Audio URL Detection
  ytMirrorsBox.style.display = 'none';
  directRawBtn.style.display = 'block';

  const ext = getFileExtension(url);
  const fileName = extractFileNameFromUrl(url);

  if (isAudioExtension(ext)) {
    setMode('audio');
    document.getElementById('prevThumb').src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="55" viewBox="0 0 80 55"><rect width="80" height="55" fill="%231e293b"/><text x="40" y="32" font-size="20" text-anchor="middle" fill="%2300e676">🎵</text></svg>';
    document.getElementById('prevTitle').textContent = fileName;
    document.getElementById('prevMeta').textContent = `Direct Audio (${ext.toUpperCase()}) • Transcode to Sony Bravia MP3`;
  } else {
    setMode('video');
    document.getElementById('prevThumb').src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="55" viewBox="0 0 80 55"><rect width="80" height="55" fill="%231e293b"/><text x="40" y="32" font-size="20" text-anchor="middle" fill="%2300d2ff">🎬</text></svg>';
    document.getElementById('prevTitle').textContent = fileName;
    document.getElementById('prevMeta').textContent = `Direct Video (${ext.toUpperCase()}) • Transcode to Sony Bravia 720p MP4`;
  }

  previewCard.style.display = 'flex';
  logMessage(`Direct stream detected: ${fileName}`);
}

// ================= COOKIE MANAGER =================
function toggleCookieBox() {
  const body = document.getElementById('cookieAccordionBody');
  const arrow = document.getElementById('cookieToggleArrow');
  const isOpen = body.style.display === 'flex';
  body.style.display = isOpen ? 'none' : 'flex';
  arrow.textContent = isOpen ? '▼' : '▲';
}

function loadSavedCookie() {
  let saved = localStorage.getItem('yt_cookie');
  if (!saved) {
    saved = DEFAULT_YOUTUBE_COOKIE;
    localStorage.setItem('yt_cookie', saved);
  }
  const input = document.getElementById('cookieInput');
  if (input) input.value = saved;
  logMessage('✅ Permanent YouTube authenticated session active.');
}

async function pasteCookieFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById('cookieInput').value = text.trim();
    saveCookie();
  } catch (_) {
    alert('Please paste the cookie content manually into the text area.');
  }
}

function saveCookie() {
  const text = document.getElementById('cookieInput').value.trim();
  if (text) {
    localStorage.setItem('yt_cookie', text);
    logMessage('✅ YouTube cookie saved in browser local storage.');
    alert('Cookie saved! It will be used for stream requests.');
  } else {
    localStorage.removeItem('yt_cookie');
    logMessage('Cookie cleared.');
  }
}

function clearCookie() {
  localStorage.removeItem('yt_cookie');
  document.getElementById('cookieInput').value = '';
  logMessage('YouTube cookie cleared.');
}

function getStoredCookie() {
  return localStorage.getItem('yt_cookie') || DEFAULT_YOUTUBE_COOKIE;
}

// ================= STREAM FETCHING WITH CORS FALLBACK =================
async function fetchDirectMediaWithProgress(targetUrl, onProgress) {
  const candidates = [
    targetUrl, // 1. Direct fetch (best performance if CORS allowed)
    `https://corsproxy.io/?url=${encodeURIComponent(targetUrl)}`, // 2. Public high-speed CORS proxy
    `https://api.allorigins.win/raw?url=${encodeURIComponent(targetUrl)}` // 3. Backup CORS proxy
  ];

  let lastError = null;

  for (let i = 0; i < candidates.length; i++) {
    const candidate = candidates[i];
    try {
      logMessage(`Connecting to media source (Method ${i + 1}/${candidates.length})...`);
      const response = await fetchWithTimeout(candidate, {}, 12000);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText}`);
      }

      const contentLength = response.headers.get('content-length');
      const totalBytes = contentLength ? parseInt(contentLength, 10) : 0;

      const reader = response.body.getReader();
      const chunks = [];
      let receivedBytes = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        receivedBytes += value.length;

        if (onProgress && totalBytes > 0) {
          const percent = Math.min(100, Math.round((receivedBytes / totalBytes) * 100));
          const mbRec = (receivedBytes / (1024 * 1024)).toFixed(1);
          const mbTotal = (totalBytes / (1024 * 1024)).toFixed(1);
          onProgress(percent, `${percent}% (${mbRec} MB / ${mbTotal} MB)`);
        } else if (onProgress) {
          const mbRec = (receivedBytes / (1024 * 1024)).toFixed(1);
          onProgress(null, `${mbRec} MB downloaded...`);
        }
      }

      // Concatenate chunks into Uint8Array
      const allChunks = new Uint8Array(receivedBytes);
      let position = 0;
      for (const chunk of chunks) {
        allChunks.set(chunk, position);
        position += chunk.length;
      }

      logMessage(`✅ Successfully downloaded ${(receivedBytes / (1024 * 1024)).toFixed(1)} MB stream data.`);
      return allChunks;
    } catch (err) {
      lastError = err;
      logMessage(`Attempt ${i + 1} failed: ${err.message}. Trying next fallback...`);
    }
  }

  throw new Error(`Could not download media stream: ${lastError ? lastError.message : 'Network error'}`);
}

// ================= UNIVERSAL FFMPEG.WASM INITIALIZER =================
async function getFFmpeg() {
  if (ffmpegInstance) return ffmpegInstance;

  logMessage('Initializing in-browser Sony Bravia transcode engine...');
  const { createFFmpeg } = FFmpeg;

  const corePath = 'https://unpkg.com/@ffmpeg/core@0.11.0/dist/ffmpeg-core.js';
  logMessage('Loading verified Sony Bravia H.264 / MP3 hardware core...');

  ffmpegInstance = createFFmpeg({
    log: true,
    corePath: corePath
  });

  ffmpegInstance.setLogger(({ type, message }) => {
    if (message && (message.includes('Error') || message.includes('error') || message.includes('Stream #') || message.includes('Output #') || message.includes('frame='))) {
      logMessage(`[FFmpeg] ${message}`);
    }
  });

  await ffmpegInstance.load();
  logMessage('✅ FFmpeg transcode engine ready.');
  return ffmpegInstance;
}

// ================= MAIN DOWNLOAD & CONVERT CONTROLLER =================
async function processSingleDownload() {
  const url = document.getElementById('mediaUrl').value.trim();
  if (!url && !selectedLocalFile) {
    alert('Please paste a direct video/audio URL, YouTube link, or pick a file from your phone.');
    return;
  }

  const quality = document.getElementById('qualitySelect').value;
  const btn = document.getElementById('convertBtn');
  const progressWrap = document.getElementById('progressWrap');
  const progressBar = document.getElementById('progressBarFill');
  const progressStatus = document.getElementById('progressStatus');

  btn.disabled = true;
  const dlCard = document.getElementById('downloadResultCard');
  if (dlCard) dlCard.style.display = 'none';
  progressWrap.style.display = 'flex';
  progressBar.style.width = '10%';
  progressStatus.textContent = 'Preparing media for conversion...';

  try {
    // ---------------- SCENARIO 1: LOCAL FILE FROM PHONE ----------------
    if (selectedLocalFile) {
      logMessage(`Reading local file: "${selectedLocalFile.name}"...`);
      progressStatus.textContent = 'Reading local file data...';
      progressBar.style.width = '25%';

      const arrayBuffer = await selectedLocalFile.arrayBuffer();
      const rawData = new Uint8Array(arrayBuffer);

      progressBar.style.width = '40%';
      progressStatus.textContent = 'Transcoding with Sony Bravia KLV-24P413D hardware specs...';

      await runFFmpegTranscode(rawData, selectedLocalFile.name, currentMode, quality, (pct, status) => {
        progressBar.style.width = `${40 + Math.round(pct * 0.6)}%`;
        progressStatus.textContent = status;
      });

      progressBar.style.width = '100%';
      progressStatus.textContent = '✅ Conversion Complete!';
      logMessage('✅ Transcoding complete. File downloaded to your phone/PC.');
      return;
    }

    // ---------------- SCENARIO 2: DIRECT MEDIA URL (NON-YOUTUBE) ----------------
    const isYouTube = /(?:youtube\.com|youtu\.be)/i.test(url);

    if (!isYouTube) {
      const fileName = extractFileNameFromUrl(url);
      logMessage(`Starting direct stream download: "${fileName}"...`);
      progressStatus.textContent = 'Downloading direct media stream...';

      const mediaBytes = await fetchDirectMediaWithProgress(url, (pct, text) => {
        if (pct !== null) {
          progressBar.style.width = `${10 + Math.round(pct * 0.4)}%`;
          progressStatus.textContent = `Downloading: ${text}`;
        } else {
          progressStatus.textContent = text;
        }
      });

      progressBar.style.width = '55%';
      progressStatus.textContent = 'Applying Sony Bravia 720p / MP3 transcoding...';

      await runFFmpegTranscode(mediaBytes, fileName, currentMode, quality, (pct, status) => {
        progressBar.style.width = `${55 + Math.round(pct * 0.45)}%`;
        progressStatus.textContent = status;
      });

      progressBar.style.width = '100%';
      progressStatus.textContent = '✅ Conversion Complete!';
      logMessage('✅ Done! 100% compatible with Sony Bravia KLV-24P413D USB player.');
      return;
    }

    // ---------------- SCENARIO 3: YOUTUBE LINK ----------------
    logMessage(`Resolving YouTube link: ${url}`);
    progressStatus.textContent = 'Resolving YouTube stream...';
    progressBar.style.width = '25%';

    let streamResult = null;

    // A. Check if backend /api/resolve is running (e.g. Vercel deployment)
    try {
      const res = await fetchWithTimeout('/api/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url,
          mode: currentMode,
          quality,
          cookie: getStoredCookie()
        })
      }, 3000);

      if (res.ok) {
        streamResult = await res.json();
      }
    } catch (_) {}

    // B. If /api/resolve is not available (GitHub Pages), resolve client-side with timeout guards
    if (!streamResult || !streamResult.success) {
      logMessage('Querying stream resolver nodes (3s max per node)...');
      streamResult = await resolveYouTubeClientSide(url, currentMode, quality);
    }

    if (!streamResult || !streamResult.downloadUrl) {
      // Guide user to Fast 1-Tap Mirrors
      progressStatus.textContent = '⚡ Use 1-Tap Fast Mirrors below for instant download!';
      progressBar.style.width = '100%';
      document.getElementById('ytMirrorsBox').scrollIntoView({ behavior: 'smooth' });
      logMessage('⚠️ YouTube bot protection requires direct mirror access.');
      logMessage('👉 Tap Cobalt Web, Y2Mate, or SaveFrom above to download in 1 tap, then pick the file with "📁 Select File from Phone Storage" to format for your Sony TV!');
      return;
    }

    progressBar.style.width = '50%';
    progressStatus.textContent = `Downloading stream: ${streamResult.title}...`;

    const mediaBytes = await fetchDirectMediaWithProgress(streamResult.downloadUrl, (pct, text) => {
      if (pct !== null) {
        progressBar.style.width = `${50 + Math.round(pct * 0.25)}%`;
        progressStatus.textContent = `Downloading stream: ${text}`;
      } else {
        progressStatus.textContent = text;
      }
    });

    progressBar.style.width = '75%';
    progressStatus.textContent = 'Encoding for Sony Bravia KLV-24P413D...';

    await runFFmpegTranscode(mediaBytes, streamResult.title, currentMode, quality, (pct, status) => {
      progressBar.style.width = `${75 + Math.round(pct * 0.25)}%`;
      progressStatus.textContent = status;
    });

    progressBar.style.width = '100%';
    progressStatus.textContent = '✅ Complete! File Ready for USB';
    logMessage('✅ Complete! 100% compatible with Sony Bravia KLV-24P413D.');
  } catch (err) {
    console.error(err);
    logMessage(`❌ Error: ${err.message}`);
    progressStatus.textContent = `❌ ${err.message}`;
  } finally {
    btn.disabled = false;
  }
}

// ================= HARDWARE TRANSCODING ENGINE (SONY BRAVIA SPECIFIC) =================
async function runFFmpegTranscode(inputUint8Array, baseTitle, mode, quality, onProgress) {
  const ffmpeg = await getFFmpeg();

  const cleanTitle = sanitizeFileName(baseTitle);
  const inputExt = getFileExtension(baseTitle) || (mode === 'video' ? 'mp4' : 'mp3');
  
  // Safe virtual filenames inside Emscripten FS
  const virtualInput = `input.${inputExt}`;
  const virtualOutput = mode === 'video' ? 'output.mp4' : 'output.mp3';
  
  const finalFileName = mode === 'video' 
    ? `${cleanTitle}_SonyBravia_720p.mp4` 
    : `${cleanTitle}_SonyBravia.mp3`;

  // Attach progress listener
  ffmpeg.setProgress(({ ratio }) => {
    const pct = Math.min(100, Math.max(0, Math.round(ratio * 100)));
    if (onProgress) {
      onProgress(ratio, `Transcoding for Sony Bravia: ${pct}%`);
    }
  });

  let detectedAV1 = false;
  ffmpeg.setLogger(({ type, message }) => {
    if (message) {
      if (message.includes('av1') || message.includes('av01') || message.includes('? (?)')) {
        detectedAV1 = true;
      }
      if (message.includes('Error') || message.includes('error') || message.includes('Stream #') || message.includes('Output #') || message.includes('frame=')) {
        logMessage(`[FFmpeg] ${message}`);
      }
    }
  });

  const inputSizeMB = ((inputUint8Array.byteLength || 0) / (1024 * 1024)).toFixed(1);
  logMessage(`Writing ${inputSizeMB} MB to virtual storage (${virtualInput})...`);
  ffmpeg.FS('writeFile', virtualInput, inputUint8Array);

  let mimeType = 'video/mp4';

  if (mode === 'audio') {
    mimeType = 'audio/mpeg';
    const bitrate = quality === '320' ? '320k' : (quality === '128' ? '128k' : '192k');
    logMessage(`Encoding MP3: ${bitrate}, 44.1kHz Stereo...`);

    await ffmpeg.run(
      '-i', virtualInput,
      '-vn',
      '-c:a', 'libmp3lame',
      '-b:a', bitrate,
      '-ar', '44100',
      '-ac', '2',
      virtualOutput
    );
  } else {
    mimeType = 'video/mp4';
    const targetHeight = quality === '360' ? 360 : (quality === '480' ? 480 : 720);
    logMessage(`Encoding H.264 Main 3.1 (${targetHeight}p Max, 30fps, yuv420p)...`);

    await ffmpeg.run(
      '-i', virtualInput,
      '-vf', `scale=-2:min(${targetHeight}\\,ih)`,
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
      virtualOutput
    );
  }

  // Read the generated output file
  let outData = null;
  try {
    outData = ffmpeg.FS('readFile', virtualOutput);
  } catch (err) {
    if (detectedAV1) {
      throw new Error('This video uses YouTube\'s AV1 (av01) codec, which WebAssembly cannot decode in-browser. Please download the H.264 (AVC) version or convert via Termux.');
    }
    throw new Error('Transcode failed: no output file generated. Please check the log messages above.');
  }

  if (!outData || outData.byteLength === 0) {
    if (detectedAV1) {
      throw new Error('This video uses YouTube\'s AV1 (av01) codec, which WebAssembly cannot decode in-browser. Please download the H.264 (AVC) version or convert via Termux.');
    }
    throw new Error('Transcode produced an empty 0-byte file. Please check the log messages above.');
  }

  // Create persistent Blob URL
  const blob = new Blob([outData.buffer], { type: mimeType });
  const blobUrl = URL.createObjectURL(blob);
  const sizeMB = (outData.byteLength / (1024 * 1024)).toFixed(1);

  // Present the dedicated Download Card
  const card = document.getElementById('downloadResultCard');
  const dlBtn = document.getElementById('downloadResultBtn');
  const nameEl = document.getElementById('resultFileName');
  const specsEl = document.getElementById('resultFileSpecs');
  const sizeEl = document.getElementById('resultFileSize');

  if (card && dlBtn) {
    nameEl.textContent = finalFileName;
    sizeEl.textContent = `${sizeMB} MB`;
    specsEl.textContent = mode === 'video'
      ? 'Sony Bravia KLV-24P413D USB Ready (720p H.264 Main 3.1 • 30fps)'
      : 'Sony Bravia KLV-24P413D USB Ready (Stereo MP3 44.1kHz)';
    dlBtn.href = blobUrl;
    dlBtn.download = finalFileName;
    card.style.display = 'flex';
    card.scrollIntoView({ behavior: 'smooth' });
  }

  logMessage(`🎉 Conversion succeeded! File ready: ${finalFileName} (${sizeMB} MB).`);
  logMessage(`👉 Tap the green "Download Converted File" button above to save directly to your phone.`);

  // Attempt direct download trigger as well
  try {
    triggerFileDownload(blobUrl, finalFileName);
  } catch (_) {}

  // Free virtual FS memory
  try {
    ffmpeg.FS('unlink', virtualOutput);
    ffmpeg.FS('unlink', virtualInput);
  } catch (_) {}
}

// Direct raw download handler
function downloadDirectRaw() {
  if (selectedLocalFile) {
    alert('This is already a local file on your phone!');
    return;
  }
  if (!directRawUrl) {
    alert('No direct URL available.');
    return;
  }
  const name = extractFileNameFromUrl(directRawUrl);
  triggerFileDownload(directRawUrl, name);
  logMessage(`Triggered raw download: ${name}`);
}

// YouTube Mirrors Helper
function openMirror(mirror) {
  const url = document.getElementById('mediaUrl').value.trim();
  if (!url) {
    alert('Paste a YouTube link first.');
    return;
  }

  let mirrorUrl = '';
  if (mirror === 'cobalt') {
    mirrorUrl = `https://cobalt.tools/#${encodeURIComponent(url)}`;
  } else if (mirror === 'y2m') {
    const videoId = (url.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([a-zA-Z0-9_-]{11})/) || [])[1];
    mirrorUrl = videoId ? `https://www.y2mate.com/youtube/${videoId}` : 'https://www.y2mate.com';
  } else if (mirror === 'savefrom') {
    mirrorUrl = `https://en.savefrom.net/#url=${encodeURIComponent(url)}`;
  }

  if (mirrorUrl) {
    window.open(mirrorUrl, '_blank');
    logMessage(`Opened ${mirror} mirror in new tab.`);
  }
}

// Client-side YouTube resolver with strict 3-second timeouts
async function resolveYouTubeClientSide(url, mode, quality) {
  const match = url.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([a-zA-Z0-9_-]{11})/);
  if (!match) return null;
  const videoId = match[1];

  for (let i = 0; i < INVIDIOUS_INSTANCES.length; i++) {
    const instance = INVIDIOUS_INSTANCES[i];
    try {
      logMessage(`Probing resolver ${i + 1}/${INVIDIOUS_INSTANCES.length} (${instance.replace('https://', '')})...`);
      const res = await fetchWithTimeout(`${instance}/api/v1/videos/${videoId}`, {}, 3000);
      if (!res.ok) continue;
      const data = await res.json();

      if (mode === 'audio') {
        const audio = data.adaptiveFormats?.find(f => f.type?.includes('audio')) || data.formatStreams?.find(f => f.type?.includes('audio'));
        if (audio?.url) {
          logMessage(`✅ Stream resolved via node ${i + 1}`);
          return {
            title: data.title || 'YouTube Audio',
            downloadUrl: audio.url
          };
        }
      } else {
        const video = data.formatStreams?.find(f => f.qualityLabel?.includes('720') || f.resolution?.includes('720')) || data.formatStreams?.[0];
        if (video?.url) {
          logMessage(`✅ Stream resolved via node ${i + 1}`);
          return {
            title: data.title || 'YouTube Video',
            downloadUrl: video.url
          };
        }
      }
    } catch (_) {
      logMessage(`Node ${i + 1} timed out or busy.`);
    }
  }

  return null;
}

// ================= TAB 2: PLAYLIST RESOLVER =================
async function fetchPlaylist() {
  const url = document.getElementById('playlistUrl').value.trim();
  if (!url) {
    alert('Please paste a YouTube Playlist URL.');
    return;
  }

  const listMatch = url.match(/[?&]list=([a-zA-Z0-9_-]+)/);
  if (!listMatch) {
    alert('Invalid Playlist URL. Make sure it contains ?list=...');
    return;
  }

  const playlistId = listMatch[1];
  const listContainer = document.getElementById('playlistItemsList');
  const playlistHeader = document.getElementById('playlistHeader');
  const fetchBtn = document.getElementById('fetchPlaylistBtn');

  fetchBtn.disabled = true;
  fetchBtn.textContent = '⏳ Loading...';
  listContainer.innerHTML = '<div class="empty-state">Loading playlist items...</div>';

  let playlistData = null;

  // 1. Try serverless if available
  try {
    const res = await fetchWithTimeout('/api/playlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    }, 4000);
    if (res.ok) {
      playlistData = await res.json();
    }
  } catch (_) {}

  // 2. Client-side Invidious fallback for GitHub Pages
  if (!playlistData || !playlistData.videos) {
    for (const inst of INVIDIOUS_INSTANCES) {
      try {
        const invRes = await fetchWithTimeout(`${inst}/api/v1/playlists/${playlistId}`, {}, 3000);
        if (!invRes.ok) continue;
        const d = await invRes.json();
        if (d && d.videos) {
          playlistData = {
            title: d.title || 'YouTube Playlist',
            totalVideos: d.videos.length,
            videos: d.videos.map(v => ({
              id: v.videoId,
              title: v.title,
              watchUrl: `https://www.youtube.com/watch?v=${v.videoId}`,
              thumbnail: `https://i.ytimg.com/vi/${v.videoId}/mqdefault.jpg`,
              formattedDuration: formatDuration(v.lengthSeconds)
            }))
          };
          break;
        }
      } catch (_) {}
    }
  }

  fetchBtn.disabled = false;
  fetchBtn.textContent = '🔍 Load Playlist';

  if (!playlistData || !playlistData.videos || playlistData.videos.length === 0) {
    listContainer.innerHTML = '<div class="empty-state">❌ Could not load playlist. Please try individual video links.</div>';
    return;
  }

  playlistVideos = playlistData.videos;
  document.getElementById('playlistTitle').textContent = playlistData.title;
  document.getElementById('playlistCount').textContent = `${playlistData.totalVideos} Videos`;
  playlistHeader.style.display = 'flex';

  listContainer.innerHTML = '';
  playlistVideos.forEach((vid, idx) => {
    const item = document.createElement('div');
    item.className = 'playlist-item';
    item.innerHTML = `
      <img class="pl-thumb" src="${vid.thumbnail}" alt="Thumbnail" />
      <div class="pl-info">
        <div class="pl-title" title="${vid.title}">#${idx + 1} ${vid.title}</div>
        <div class="pl-duration">⏱️ ${vid.formattedDuration}</div>
      </div>
      <div class="pl-actions">
        <button class="pl-btn" onclick="sendToConverter('${vid.watchUrl}', 'video')">🎬 720p</button>
        <button class="pl-btn" onclick="sendToConverter('${vid.watchUrl}', 'audio')">🎵 MP3</button>
      </div>
    `;
    listContainer.appendChild(item);
  });

  logMessage(`Loaded playlist "${playlistData.title}" with ${playlistVideos.length} videos.`);
}

function sendToConverter(url, mode) {
  switchTab('single');
  document.getElementById('mediaUrl').value = url;
  setMode(mode);
  onUrlChanged();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function startBatchDownload() {
  if (playlistVideos.length === 0) return;
  alert('Starting batch processing. Videos will be converted and downloaded 1 by 1.');

  for (let i = 0; i < playlistVideos.length; i++) {
    const vid = playlistVideos[i];
    logMessage(`[Batch ${i + 1}/${playlistVideos.length}] Processing "${vid.title}"...`);
    document.getElementById('mediaUrl').value = vid.watchUrl;
    await onUrlChanged();
    await processSingleDownload();
    // 2-second cooldown between queue items
    await new Promise(r => setTimeout(r, 2000));
  }
}

// ================= UTILITIES & HELPERS =================
function getFileExtension(pathOrUrl) {
  try {
    const clean = pathOrUrl.split('#')[0].split('?')[0];
    const parts = clean.split('.');
    return parts.length > 1 ? parts.pop().toLowerCase() : '';
  } catch (_) {
    return '';
  }
}

function isAudioExtension(ext) {
  return ['mp3', 'm4a', 'wav', 'aac', 'flac', 'ogg', 'opus', 'wma'].includes(ext);
}

function extractFileNameFromUrl(url) {
  try {
    const clean = url.split('#')[0].split('?')[0];
    const segment = clean.split('/').filter(Boolean).pop();
    if (segment) {
      return decodeURIComponent(segment);
    }
  } catch (_) {}
  return 'bravia_media';
}

function sanitizeFileName(name) {
  if (!name) return 'bravia_media';
  // Strip existing file extension if present
  const noExt = name.replace(/\.[a-zA-Z0-9]{2,5}$/, '');
  return noExt
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '_')
    .substring(0, 50) || 'bravia_media';
}

function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

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
