const CACHE_NAME = "gulbeeledger-v3";

const OFFLINE_URL = "/user/";

const FILES_TO_CACHE = [
    "/",
    "/user/",
    "/static/manifest.json",
    "/static/icons/icon-192.png",
    "/static/icons/icon-512.png",
    "/static/icons/maskable-192.png",
    "/static/icons/maskable-512.png",
    "/static/icons/favicon-32.png"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(FILES_TO_CACHE))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys()
            .then(keys => {
                return Promise.all(
                    keys
                        .filter(key => key !== CACHE_NAME)
                        .map(key => caches.delete(key))
                );
            })
            .then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", event => {

    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(response => {

                // Cache successful responses
                if (response && response.status === 200) {
                    const responseClone = response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseClone);
                        });
                }

                return response;
            })
            .catch(() => {

                return caches.match(event.request)
                    .then(cachedResponse => {

                        if (cachedResponse) {
                            return cachedResponse;
                        }

                        // For navigation requests, show cached app page
                        if (event.request.mode === "navigate") {
                            return caches.match(OFFLINE_URL);
                        }

                        return new Response(
                            "You are offline.",
                            {
                                status: 503,
                                headers: {
                                    "Content-Type": "text/plain"
                                }
                            }
                        );
                    });
            })
    );
});