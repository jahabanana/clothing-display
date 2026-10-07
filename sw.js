// Kleidungs-Kiosk Service Worker
// Jede Änderung an index.html erfordert eine neue CACHE_VERSION hier (§4.2).
const CACHE_VERSION = 'v5';
const CACHE_NAME = `kiosk-${CACHE_VERSION}`;

const APP_SHELL = [
  './',
  'index.html',
  'manifest.json',
  'icon-180.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL.map((url) => new Request(url, { cache: 'reload' }))))   // am HTTP-Cache vorbei, sonst kann bei zwei Deploys kurz nacheinander ein alter Stand hängen bleiben
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Nur eigene Origin behandeln, andere (Open-Meteo) durchlassen.
  if (new URL(request.url).origin !== self.location.origin) return;

  event.respondWith(
    caches.match(request, { ignoreSearch: request.mode === 'navigate' })
      .then((cached) => cached || fetch(request))
  );
});
