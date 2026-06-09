const CACHE_NAME = "expense-tracker-v3";
const CORE_ASSETS = [
  "/",
  "/login",
  "/static/style.css?v=2.0.1",
  "/static/app.js?v=2.0.1",
  "/static/manifest.webmanifest"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      const promises = CORE_ASSETS.map(asset => {
        return fetch(new Request(asset, { cache: "reload" }))
          .then(res => {
            if (res.ok) {
              return cache.put(asset, res);
            }
            throw new Error(`Failed to fetch: ${asset}`);
          });
      });
      return Promise.all(promises);
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
  if (request.method !== "GET") {
    return;
  }

  event.respondWith(
    fetch(request)
      .then(response => {
        const url = new URL(request.url);
        if (
          url.origin === self.location.origin &&
          url.pathname.startsWith("/static/") &&
          response.status === 200
        ) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, responseClone));
        }
        return response;
      })
      .catch(() => caches.match(request).then(cached => cached || caches.match("/")))
  );
});
