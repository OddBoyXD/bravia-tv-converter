// api/playlist.js - YouTube Playlist Resolver for Batch & 1-by-1 Downloads
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { url } = req.method === 'POST' ? req.body : req.query;

  if (!url) {
    return res.status(400).json({ error: 'Missing playlist URL' });
  }

  // Extract playlist ID
  const match = url.match(/[?&]list=([a-zA-Z0-9_-]+)/);
  if (!match) {
    return res.status(400).json({ error: 'Invalid playlist URL. Make sure it contains ?list=...' });
  }

  const playlistId = match[1];

  // List of public Invidious instances to scrape playlist metadata reliably
  const INVIDIOUS_INSTANCES = [
    'https://invidious.nerdvpn.de',
    'https://inv.tux.pizza',
    'https://vid.puffyan.us',
    'https://yt.drgnz.club'
  ];

  for (const instance of INVIDIOUS_INSTANCES) {
    try {
      const response = await fetch(`${instance}/api/v1/playlists/${playlistId}`, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
      });

      if (!response.ok) continue;

      const data = await response.json();
      if (data && data.videos && Array.isArray(data.videos)) {
        const videos = data.videos.map(v => ({
          id: v.videoId,
          title: v.title,
          author: v.author,
          lengthSeconds: v.lengthSeconds,
          formattedDuration: formatDuration(v.lengthSeconds),
          thumbnail: `https://i.ytimg.com/vi/${v.videoId}/mqdefault.jpg`,
          watchUrl: `https://www.youtube.com/watch?v=${v.videoId}`
        }));

        return res.status(200).json({
          success: true,
          playlistId: playlistId,
          title: data.title || 'YouTube Playlist',
          author: data.author || 'Unknown Creator',
          totalVideos: videos.length,
          videos: videos
        });
      }
    } catch (_) {}
  }

  // Fallback: Return a sample extraction if external instances are restricted
  return res.status(502).json({
    error: 'Could not fetch playlist metadata from public nodes. Please try again or paste individual video links.'
  });
}

function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}
