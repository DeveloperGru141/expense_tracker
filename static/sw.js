const CACHE_NAME = "expense-tracker-v4";
const CORE_ASSETS = [
  "/",
  "/login",
  "/register",
  "/static/style.css",
  "/static/app.js",
  "/static/manifest.webmanifest"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(CORE_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const { request } = event;
  
  // Cache-first for static assets
  if (request.url.includes("/static/")) {
    event.respondWith(
      caches.match(request).then(cached => {
        return cached || fetch(request).then(response => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, responseClone));
          return response;
        });
      })
    );
    return;
  }

  // Network-first for navigation and dynamic pages
  event.respondWith(
    fetch(request)
      .then(response => {
        return response;
      })
      .catch(() => caches.match(request))
  );
});
