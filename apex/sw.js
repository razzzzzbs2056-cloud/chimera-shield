/* Apex service worker: cache-first app shell so the app works fully offline. */
const CACHE = 'apex-v3';
const ASSETS = [
  './', 'index.html', 'manifest.webmanifest', 'icons/icon.svg', 'css/styles.css',
  'js/core/store.js', 'js/core/registry.js', 'js/core/ui.js', 'js/core/knowledge.js', 'js/core/app.js',
  'js/modules/bootcamp.js', 'js/modules/pt.js', 'js/modules/character.js',
  'js/modules/sleep.js', 'js/modules/fitness.js', 'js/modules/nutrition.js',
  'js/modules/mindset.js', 'js/modules/learning.js', 'js/modules/digital.js',
  'js/modules/focus.js', 'js/modules/goals.js', 'js/modules/habits.js',
  'js/modules/finance.js', 'js/modules/social.js', 'js/modules/review.js',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Network-first so updates show up immediately when online; cache is the offline fallback.
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match('index.html')))
  );
});
