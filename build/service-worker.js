/* Minimal service worker placeholder for build */
self.addEventListener('install', event => {
  self.skipWaiting();
});
self.addEventListener('activate', event => {
  clients.claim();
});
