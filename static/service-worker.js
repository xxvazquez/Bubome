self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('inventory-app-cache').then((cache) => {
      return cache.addAll([
        '/',
        '/static/styles.css',
        '/static/icon-192x192.png',
        '/static/icon-512x512.png',
        '/static/manifest.json'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});
