// static/js/serviceworker.js - Enhanced version
const CACHE_NAME = 'mgpas-v2';
const API_CACHE = 'mgpas-api-v1';
const urlsToCache = [
    '/',
    '/static/css/styles.css',
    '/static/js/app.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/auth/login/',
    '/dashboard/',
    '/grading/students/'
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - enhanced for API calls
self.addEventListener('fetch', event => {
    // Handle API requests
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Clone the response to store it
                    const responseClone = response.clone();
                    caches.open(API_CACHE)
                        .then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    return response;
                })
                .catch(() => {
                    // If network fails, try to get from cache
                    return caches.match(event.request)
                        .then(response => {
                            return response || new Response(JSON.stringify({error: 'Network failed and no cached data available'}), {
                                status: 503,
                                headers: new Headers({'Content-Type': 'application/json'})
                            });
                        });
                })
        );
    } else {
        // Handle other requests (static assets, pages)
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    // Return cached version or fetch from network
                    return response || fetch(event.request)
                        .then(response => {
                            // Don't cache non-GET requests or non-200 responses
                            if (event.request.method !== 'GET' || !response || response.status !== 200) {
                                return response;
                            }
                            
                            // Clone the response to store it
                            const responseToCache = response.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => {
                                    cache.put(event.request, responseToCache);
                                });
                            
                            return response;
                        });
                })
        );
    }
});

// Background sync for offline data
self.addEventListener('sync', event => {
    if (event.tag === 'sync-pending-requests') {
        event.waitUntil(syncPendingRequests());
    }
});

// Function to sync pending requests when online
function syncPendingRequests() {
    return getPendingRequests().then(requests => {
        const promises = requests.map(request => {
            return fetch(request.url, {
                method: request.method,
                headers: new Headers(request.headers),
                body: request.body
            })
            .then(response => {
                if (response.ok) {
                    // Remove from pending requests if successful
                    return removePendingRequest(request.id);
                }
                throw new Error('Sync failed');
            });
        });
        
        return Promise.all(promises);
    });
}

// Helper functions for pending requests (simplified version)
function getPendingRequests() {
    // In a real implementation, you would use IndexedDB
    return Promise.resolve([]);
}

function removePendingRequest(id) {
    return Promise.resolve();
}