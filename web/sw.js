/*
 * Service worker do Wine Rate.
 * Objetivo: tornar o site instalável e mostrar uma página amigável sem internet.
 * Não guarda páginas nem respostas da API, para não expor dados de um usuário
 * a outro no mesmo aparelho nem mostrar informação desatualizada.
 */
const CACHE = "winerate-offline-v1";
const OFFLINE_URL = "/offline/";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.add(OFFLINE_URL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.mode !== "navigate") return;   // só páginas; nada de API
  event.respondWith(fetch(event.request).catch(() => caches.match(OFFLINE_URL)));
});
