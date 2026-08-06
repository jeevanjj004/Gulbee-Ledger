const CACHE_NAME = "gulbeeledger-v2";

const FILES_TO_CACHE = [
    "/",
    "/user/",
    "/static/manifest.json",
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(FILES_TO_CACHE))
    );
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME)
                        return caches.delete(key);
                })
            )
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", event => {

    if (event.request.method !== "GET")
        return;

    event.respondWith(

        fetch(event.request)
            .then(response => {

                let copy = response.clone();

                caches.open(CACHE_NAME)
                    .then(cache => cache.put(event.request, copy));

                return response;

            })

            .catch(() => {

                return caches.match(event.request)
                    .then(res => {

                        if (res)
                            return res;

                        return caches.match("/user/");

                    });

            })

    );

});