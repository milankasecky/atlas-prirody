// Service worker Atlasu přírody.
// Umožňuje aplikaci fungovat i úplně bez internetu.

const NAZEV_CACHE = "atlas-prirody-cache";

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

// Strategie "nejdřív síť": když je internet k dispozici, použije se vždy
// čerstvá odpověď (a uloží se do cache pro příště). Když internet není,
// vrátí se poslední uložená verze z cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request)
      .then((odpoved) => {
        const kopieProCache = odpoved.clone();
        caches.open(NAZEV_CACHE).then((cache) => cache.put(event.request, kopieProCache));
        return odpoved;
      })
      .catch(() => caches.match(event.request))
  );
});
