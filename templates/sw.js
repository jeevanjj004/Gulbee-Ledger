const CACHE_NAME = "gulbeeledger-v4";

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


// ===============================
// INSTALL
// ===============================

self.addEventListener("install", function (event) {

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(function (cache) {

                return cache.addAll(FILES_TO_CACHE);

            })
            .then(function () {

                return self.skipWaiting();

            })

    );

});


// ===============================
// ACTIVATE
// ===============================

self.addEventListener("activate", function (event) {

    event.waitUntil(

        caches.keys()
            .then(function (cacheNames) {

                return Promise.all(

                    cacheNames
                        .filter(function (cacheName) {

                            return cacheName !== CACHE_NAME;

                        })
                        .map(function (cacheName) {

                            return caches.delete(cacheName);

                        })

                );

            })
            .then(function () {

                return self.clients.claim();

            })

    );

});


// ===============================
// FETCH
// ===============================

self.addEventListener("fetch", function (event) {

    // Only handle GET requests
    if (event.request.method !== "GET") {
        return;
    }


    event.respondWith(

        fetch(event.request)

            .then(function (response) {

                // Cache successful responses
                if (
                    response &&
                    response.status === 200 &&
                    response.type !== "opaque"
                ) {

                    const responseClone =
                        response.clone();

                    caches.open(CACHE_NAME)
                        .then(function (cache) {

                            cache.put(
                                event.request,
                                responseClone
                            );

                        });

                }

                return response;

            })

            .catch(function () {

                return caches.match(event.request)

                    .then(function (cachedResponse) {

                        if (cachedResponse) {
                            return cachedResponse;
                        }


                        // If the user opens a page
                        // while offline
                        if (
                            event.request.mode === "navigate"
                        ) {

                            return caches.match(
                                OFFLINE_URL
                            );

                        }


                        // Fallback response
                        return new Response(
                            "You are offline.",
                            {
                                status: 503,
                                headers: {
                                    "Content-Type":
                                        "text/plain"
                                }
                            }
                        );

                    });

            })

    );

});