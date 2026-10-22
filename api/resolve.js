// api/resolve.js - Resolves YouTube and Media streams with Sony Bravia 720p / MP3 compliance
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { url, mode, quality } = req.method === 'POST' ? req.body : req.query;

  if (!url) {
    return res.status(400).json({ error: 'Missing media URL' });
  }

  try {
    // 1. Check if it is a YouTube URL
    const isYouTube = /(?:youtube\.com|youtu\.be)/i.test(url);

    if (isYouTube) {
      return await resolveYouTubeStream(url, mode || 'video', quality || '720', res);
    } else {
      // 2. Direct Media URL (MKV, MP4, MOV, WEBM, MP3, etc.)
      return await resolveDirectMedia(url, mode || 'video', quality || '720', res);
    }
  } catch (err) {
    console.error('Resolve Error:', err);
    return res.status(500).json({ error: 'Failed to process media stream', details: err.message });
  }
}

// Multiple public, reliable Cobalt instances with automatic failover
const COBALT_INSTANCES = [
  'https://cobalt-api.kwiatekm.tokyo',
  'https://api.cobalt.tools',
  'https://cobalt.canine.tools',
  'https://cobalt.synced.club',
  'https://cobalt.directory'
];

async function resolveYouTubeStream(url, mode, quality, res) {
  // Extract video ID for metadata
  let videoId = null;
  const match = url.match(/(?:v=|youtu\.be\/|shorts\/|embed\/)([a-zA-Z0-9_-]{11})/);
  if (match) videoId = match[1];

  let meta = {
    title: 'YouTube Video',
    author: 'Unknown Creator',
    duration: 180,
    thumbnail: videoId ? `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg` : ''
  };

  // Fetch basic metadata from noembed if available
  try {
    const oembedRes = await fetch(`https://noembed.com/embed?url=${encodeURIComponent(url)}`);
    if (oembedRes.ok) {
      const oembed = await oembedRes.json();
      if (oembed.title) meta.title = oembed.title;
      if (oembed.author_name) meta.author = oembed.author_name;
    }
  } catch (_) {}

  // Sony Bravia KLV-24P413D Constraints:
  // Video: Max 720p, H.264 (AVC)
  // Audio: MP3 (320, 192, 128)
  const isAudioOnly = mode === 'audio';

  // Map quality to valid parameters
  let targetQuality = '720';
  if (quality === '480' || quality === '360') targetQuality = quality;

  let targetBitrate = '192';
  if (quality === '320' || quality === '128') targetBitrate = quality;

  const payload = {
    url: url,
    videoQuality: targetQuality,
    youtubeVideoCodec: 'h264',
    downloadMode: isAudioOnly ? 'audio' : 'auto',
    audioFormat: 'mp3',
    audioBitrate: targetBitrate
  };

  // Try each Cobalt instance with fallback
  let downloadUrl = null;
  let lastError = null;

  for (const instance of COBALT_INSTANCES) {
    try {
      const response = await fetch(instance, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) continue;

      const data = await response.json();
      if (data && (data.status === 'redirect' || data.status === 'stream' || data.status === 'tunnel') && data.url) {
        downloadUrl = data.url;
        break;
      }
    } catch (e) {
      lastError = e;
    }
  }

  // Calculate estimated file size
  // Formula: (bitrate kbps * duration seconds) / 8 = KB
  let estBitrateKbps = isAudioOnly ? parseInt(targetBitrate, 10) : (targetQuality === '720' ? 2400 : targetQuality === '480' ? 1200 : 700);
  let estSizeMB = ((estBitrateKbps * (meta.duration || 210)) / (8 * 1024)).toFixed(1);

  if (downloadUrl) {
    return res.status(200).json({
      success: true,
      type: 'youtube',
      mode: isAudioOnly ? 'audio' : 'video',
      quality: isAudioOnly ? `${targetBitrate} kbps MP3` : `${targetQuality}p HD (H.264)`,
      title: meta.title,
      author: meta.author,
      thumbnail: meta.thumbnail,
      estimatedSizeMB: `${estSizeMB} MB`,
      downloadUrl: downloadUrl,
      tvCompatible: true,
      targetDevice: 'Sony Bravia KLV-24P413D'
    });
  }

  // Fallback to Invidious/Piped stream URL construction if Cobalt is congested
  const pipedStreamUrl = `https://pipedapi.kavin.rocks/streams/${videoId}`;
  try {
    const pipedRes = await fetch(pipedStreamUrl);
    if (pipedRes.ok) {
      const pipedData = await pipedRes.json();
      meta.title = pipedData.title || meta.title;
      meta.author = pipedData.uploader || meta.author;
      meta.duration = pipedData.duration || meta.duration;

      if (isAudioOnly) {
        const audioStream = pipedData.audioStreams?.find(s => s.format === 'M4A' || s.codec === 'opus') || pipedData.audioStreams?.[0];
        if (audioStream?.url) {
          return res.status(200).json({
            success: true,
            type: 'stream',
            mode: 'audio',
            quality: `${targetBitrate} kbps MP3`,
            title: meta.title,
            thumbnail: meta.thumbnail,
            estimatedSizeMB: `${estSizeMB} MB`,
            downloadUrl: audioStream.url,
            needsTranscode: true // Browser FFmpeg will ensure MP3 transcode for Sony TV
          });
        }
      } else {
        const videoStream = pipedData.videoStreams?.find(s => s.quality === `${targetQuality}p` && s.videoOnly === false) || pipedData.videoStreams?.[0];
        if (videoStream?.url) {
          return res.status(200).json({
            success: true,
            type: 'stream',
            mode: 'video',
            quality: `${targetQuality}p HD`,
            title: meta.title,
            thumbnail: meta.thumbnail,
            estimatedSizeMB: `${estSizeMB} MB`,
            downloadUrl: videoStream.url,
            needsTranscode: false
          });
        }
      }
    }
  } catch (_) {}

  return res.status(502).json({
    error: 'Could not fetch stream at this moment. Please retry in a few seconds.',
    details: lastError ? lastError.message : 'Instances busy'
  });
}

async function resolveDirectMedia(url, mode, quality, res) {
  // Direct file URL (MKV, MOV, WEBM, FLV, MP4, MP3)
  const isAudio = mode === 'audio';
  const fileName = url.split('/').pop().split('?')[0] || (isAudio ? 'audio.mp3' : 'video.mp4');

  return res.status(200).json({
    success: true,
    type: 'direct',
    mode: isAudio ? 'audio' : 'video',
    quality: isAudio ? `${quality || 192} kbps MP3` : `${quality || 720}p HD (H.264)`,
    title: decodeURIComponent(fileName),
    downloadUrl: url,
    needsTranscode: true, // Will run through in-browser FFmpeg.wasm for strict 720p/MP3 Sony TV compliance
    estimatedSizeMB: 'Calculated on stream'
  });
}
