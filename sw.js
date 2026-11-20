// 韓國旅遊地圖 — Service Worker（離線功能）
// 網頁本體：有網路時抓最新版，沒網路時用快取
// 地圖圖磚：先用快取（離線地圖下載的就存在這裡）
// 搜尋／路線／翻譯：先連網路，失敗時用上次的結果
const VER = 'kmap-v5';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];
const TILE_HOSTS = ['tiles.openfreemap.org', 'tile.openstreetmap.fr', 'tile.opentopomap.org', 'server.arcgisonline.com'];
const API_HOSTS = ['nominatim.openstreetmap.org', 'routing.openstreetmap.de', 'api.transitous.org', 'translate.googleapis.com',
  'api.mymemory.translated.net', 'open.er-api.com', 'overpass-api.de', 'api.open-meteo.com', 'air-quality-api.open-meteo.com', 'maps.mail.ru', 'overpass.private.coffee'];
const MAX_API_ENTRIES = 400;
const TILE_CACHE = 'kmap-tiles';   // 固定名稱：更新網頁版本時保留已下載的離線地圖
const LIB_CACHE = 'kmap-libs';     // 拍照辨識程式與韓文辨識資料（固定版本，下載一次就離線可用）

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VER + '-shell').then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('kmap-') && !k.startsWith(VER) && k !== TILE_CACHE && k !== LIB_CACHE && !k.endsWith('-tiles')).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function isStaticTile(u){
  if (u.hostname === 'server.arcgisonline.com') return true;
  return /\.(pbf|png|jpe?g|webp|mvt)$/i.test(u.pathname) || /\/(fonts|sprites)\//.test(u.pathname);
}
async function cacheFirst(req, name){
  const c = await caches.open(name);
  const hit = await caches.match(req);   // 所有快取都找（含舊版本下載的離線地圖）
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok) c.put(req, res.clone());
  return res;
}
async function networkFirst(req, name, timeout = 8000, limit = 0){
  const c = await caches.open(name);
  try {
    const res = await Promise.race([fetch(req), new Promise((_, no) => setTimeout(() => no(new Error('timeout')), timeout))]);
    if (res.ok) {
      c.put(req, res.clone());
      if (limit) c.keys().then(ks => { if (ks.length > limit) ks.slice(0, ks.length - limit).forEach(k => c.delete(k)); });
    }
    return res;
  } catch (err) {
    const hit = await c.match(req, { ignoreVary:true });
    if (hit) return hit;
    throw err;
  }
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (u.origin === self.location.origin) {
    e.respondWith(networkFirst(req, VER + '-shell', 4000).catch(() => caches.match('./index.html')));
    return;
  }
  if (TILE_HOSTS.some(h => u.hostname === h || u.hostname.endsWith('.' + h))) {
    e.respondWith(isStaticTile(u) ? cacheFirst(req, TILE_CACHE) : networkFirst(req, TILE_CACHE));
    return;
  }
  if (u.hostname === 'cdn.jsdelivr.net' && /tesseract/.test(u.pathname)) {
    e.respondWith(cacheFirst(req, LIB_CACHE));
    return;
  }
  if (API_HOSTS.some(h => u.hostname === h)) {
    const timeout = /overpass|maps\.mail\.ru/.test(u.hostname) ? 130000 : u.hostname === 'api.transitous.org' ? 30000 : 12000;
    e.respondWith(networkFirst(req, VER + '-api', timeout, MAX_API_ENTRIES));
  }
});
