/**
 * AGRI B2B Service Worker - Enhanced Version
 * Enables offline functionality, caching, push notifications, and advanced PWA features
 * Version: 2.0.0
 */

const CACHE_VERSION = 'v2';
const CACHE_NAME = `agri-b2b-cache-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline/';
const MAX_CACHE_AGE = 7 * 24 * 60 * 60 * 1000; // 7 days

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/shop/',
  '/offline/',
  '/static/css/custom.css',
  '/static/css/utilities.css',
  '/static/js/main.js',
  '/static/js/pwa-install.js',
  '/static/js/pwa-enhanced.js',
  '/static/manifest.json',
  '/static/images/pwa/icon-192x192.png',
  '/static/images/pwa/icon-512x512.png'
];

// Routes that should always fetch from network
const NETWORK_ONLY_ROUTES = [
  '/api/v1/auth/',
  '/api/start_order/',
  '/admin/',
  '/api/pwa-analytics/'
];

// Routes that should use stale-while-revalidate
const SWR_ROUTES = [
  '/api/v1/products/',
  '/api/v1/categories/',
  '/api/v1/deals/',
  '/api/v1/trending/'
];

/**
 * Install Event - Precache essential assets
 */
self.addEventListener('install', (event) => {
  console.log('[SW v2] Installing Service Worker...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async (cache) => {
        console.log('[SW v2] Precaching app shell...');

        // Cache assets one by one to handle failures gracefully
        const results = await Promise.allSettled(
          PRECACHE_ASSETS.map(async (url) => {
            try {
              const response = await fetch(url);
              if (response.ok) {
                await cache.put(url, response);
                return { url, success: true };
              }
              return { url, success: false, status: response.status };
            } catch (error) {
              console.warn(`[SW v2] Failed to cache: ${url}`, error.message);
              return { url, success: false, error: error.message };
            }
          })
        );

        const successful = results.filter(r => r.value?.success).length;
        console.log(`[SW v2] Precached ${successful}/${PRECACHE_ASSETS.length} assets`);

        return results;
      })
      .then(() => self.skipWaiting())
  );
});

/**
 * Activate Event - Clean up old caches
 */
self.addEventListener('activate', (event) => {
  console.log('[SW v2] Activating Service Worker...');

  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName.startsWith('agri-b2b-cache-') && cacheName !== CACHE_NAME) {
              console.log('[SW v2] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Clean up expired cache entries
      cleanExpiredCacheEntries(),
      // Claim clients immediately
      self.clients.claim()
    ])
  );
});

/**
 * Clean expired cache entries
 */
async function cleanExpiredCacheEntries() {
  const cache = await caches.open(CACHE_NAME);
  const requests = await cache.keys();
  const now = Date.now();

  for (const request of requests) {
    const response = await cache.match(request);
    if (response) {
      const dateHeader = response.headers.get('date');
      if (dateHeader) {
        const cacheDate = new Date(dateHeader).getTime();
        if (now - cacheDate > MAX_CACHE_AGE) {
          await cache.delete(request);
          console.log('[SW v2] Deleted expired cache:', request.url);
        }
      }
    }
  }
}

/**
 * Fetch Event - Handle network requests with appropriate caching strategy
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http requests
  if (!request.url.startsWith('http')) {
    return;
  }

  // Network only routes
  if (NETWORK_ONLY_ROUTES.some(route => url.pathname.startsWith(route))) {
    event.respondWith(fetch(request));
    return;
  }

  // Skip cross-origin requests (except allowed CDNs)
  const allowedOrigins = [
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'cdn.jsdelivr.net',
    'js.stripe.com'
  ];

  if (url.origin !== location.origin &&
      !allowedOrigins.some(origin => url.hostname.includes(origin))) {
    return;
  }

  // Determine strategy and respond
  event.respondWith(handleFetch(request, url));
});

/**
 * Handle fetch with appropriate strategy
 */
async function handleFetch(request, url) {
  // Navigation requests - Network first with offline fallback
  if (request.mode === 'navigate') {
    return handleNavigationRequest(request);
  }

  // API requests with SWR
  if (SWR_ROUTES.some(route => url.pathname.startsWith(route))) {
    return staleWhileRevalidate(request);
  }

  // Static assets - Cache first
  if (url.pathname.startsWith('/static/') ||
      url.pathname.startsWith('/media/') ||
      url.pathname.match(/\.(png|jpg|jpeg|gif|webp|svg|ico)$/)) {
    return cacheFirst(request);
  }

  // CSS, JS, Fonts - Stale while revalidate
  if (url.pathname.match(/\.(css|js|woff2?|ttf|otf)$/) ||
      url.hostname.includes('fonts')) {
    return staleWhileRevalidate(request);
  }

  // Default - Network first
  return networkFirst(request);
}

/**
 * Handle navigation requests with offline support
 */
async function handleNavigationRequest(request) {
  try {
    // Try to fetch from network
    const networkResponse = await fetch(request);

    // Cache successful navigation responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[SW v2] Navigation failed, trying cache:', request.url);

    // Try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline page
    const offlinePage = await caches.match(OFFLINE_URL);
    if (offlinePage) {
      return offlinePage;
    }

    // Last resort - return a basic offline response
    return new Response(
      '<html><body><h1>Offline</h1><p>Please check your connection.</p></body></html>',
      { headers: { 'Content-Type': 'text/html' } }
    );
  }
}

/**
 * Network First Strategy
 */
async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

/**
 * Cache First Strategy
 */
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);

  if (cachedResponse) {
    // Refresh cache in background
    fetch(request).then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse);
      }
    }).catch(() => {});

    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('[SW v2] Cache first failed:', error);
    throw error;
  }
}

/**
 * Stale While Revalidate Strategy
 */
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);

  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch((error) => {
    console.warn('[SW v2] SWR fetch failed:', error);
    return null;
  });

  return cachedResponse || await fetchPromise;
}

/**
 * Background Sync - Handle offline actions
 */
self.addEventListener('sync', (event) => {
  console.log('[SW v2] Background sync:', event.tag);

  switch (event.tag) {
    case 'sync-cart':
      event.waitUntil(syncCart());
      break;
    case 'sync-wishlist':
      event.waitUntil(syncWishlist());
      break;
    case 'sync-analytics':
      event.waitUntil(syncAnalytics());
      break;
    default:
      console.log('[SW v2] Unknown sync tag:', event.tag);
  }
});

async function syncCart() {
  console.log('[SW v2] Syncing cart data...');
  const pendingCart = await getFromIndexedDB('pending-cart');
  if (pendingCart) {
    try {
      await fetch('/api/v1/cart/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pendingCart)
      });
      await deleteFromIndexedDB('pending-cart');
    } catch (error) {
      console.error('[SW v2] Cart sync failed:', error);
    }
  }
}

async function syncWishlist() {
  console.log('[SW v2] Syncing wishlist data...');
  // Implementation similar to syncCart
}

async function syncAnalytics() {
  console.log('[SW v2] Syncing analytics data...');
  const pendingAnalytics = await getFromIndexedDB('pending-analytics');
  if (pendingAnalytics && pendingAnalytics.length > 0) {
    try {
      for (const event of pendingAnalytics) {
        await fetch('/api/pwa-analytics/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(event)
        });
      }
      await deleteFromIndexedDB('pending-analytics');
    } catch (error) {
      console.error('[SW v2] Analytics sync failed:', error);
    }
  }
}

/**
 * Periodic Background Sync
 */
self.addEventListener('periodicsync', (event) => {
  console.log('[SW v2] Periodic sync:', event.tag);

  if (event.tag === 'content-sync') {
    event.waitUntil(refreshContent());
  }
});

async function refreshContent() {
  console.log('[SW v2] Refreshing content...');

  const cache = await caches.open(CACHE_NAME);
  const urlsToRefresh = [
    '/api/v1/deals/',
    '/api/v1/trending/',
    '/api/v1/flash-sales/'
  ];

  for (const url of urlsToRefresh) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        await cache.put(url, response);
      }
    } catch (error) {
      console.warn('[SW v2] Content refresh failed for:', url);
    }
  }
}

/**
 * Push Notifications
 */
self.addEventListener('push', (event) => {
  console.log('[SW v2] Push notification received');

  let data = {
    title: 'AGRI B2B',
    body: 'You have a new notification',
    icon: '/static/images/pwa/icon-192x192.png',
    badge: '/static/images/pwa/icon-72x72.png',
    tag: 'default',
    data: {}
  };

  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    tag: data.tag,
    vibrate: [100, 50, 100],
    data: {
      ...data.data,
      dateOfArrival: Date.now()
    },
    actions: data.actions || [
      { action: 'view', title: 'View' },
      { action: 'dismiss', title: 'Dismiss' }
    ],
    requireInteraction: data.requireInteraction || false
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

/**
 * Notification Click Handler
 */
self.addEventListener('notificationclick', (event) => {
  console.log('[SW v2] Notification click:', event.action);

  event.notification.close();

  const urlToOpen = event.notification.data?.url || '/';

  if (event.action === 'dismiss') {
    return;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(urlToOpen);
            return client.focus();
          }
        }
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

/**
 * Notification Close Handler
 */
self.addEventListener('notificationclose', (event) => {
  console.log('[SW v2] Notification closed');
  // Track notification dismissals for analytics
});

/**
 * Message Handler - Communicate with main thread
 */
self.addEventListener('message', (event) => {
  // Validate source - ensure message comes from a controlled client
  // In Service Workers, event.origin is not available; we verify the source instead
  if (!event.source || event.source.type !== 'window') {
    console.warn('[SW v2] Message rejected: Invalid source type');
    return;
  }

  // Additional validation: ensure the source URL is from same origin
  try {
    const sourceUrl = new URL(event.source.url);
    if (sourceUrl.origin !== self.location.origin) {
      console.warn('[SW v2] Message rejected: Cross-origin source');
      return;
    }
  } catch (e) {
    console.warn('[SW v2] Message rejected: Unable to validate source URL');
    return;
  }

  console.log('[SW v2] Message received:', event.data);

  const { type, payload } = event.data || {};

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'CACHE_URLS':
      event.waitUntil(
        caches.open(CACHE_NAME)
          .then((cache) => cache.addAll(payload.urls))
      );
      break;

    case 'CLEAR_CACHE':
      event.waitUntil(caches.delete(CACHE_NAME));
      break;

    case 'GET_CACHE_SIZE':
      getCacheSize().then((size) => {
        event.ports[0].postMessage({ size });
      });
      break;

    case 'PREFETCH':
      event.waitUntil(prefetchUrls(payload.urls));
      break;

    default:
      console.log('[SW v2] Unknown message type:', type);
  }
});

/**
 * Get cache size
 */
async function getCacheSize() {
  const cache = await caches.open(CACHE_NAME);
  const requests = await cache.keys();
  let totalSize = 0;

  for (const request of requests) {
    const response = await cache.match(request);
    if (response) {
      const blob = await response.clone().blob();
      totalSize += blob.size;
    }
  }

  return totalSize;
}

/**
 * Prefetch URLs
 */
async function prefetchUrls(urls) {
  const cache = await caches.open(CACHE_NAME);

  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        await cache.put(url, response);
      }
    } catch (error) {
      console.warn('[SW v2] Prefetch failed for:', url);
    }
  }
}

/**
 * IndexedDB helpers for offline data
 */
const DB_NAME = 'agri-b2b-sw';
const DB_VERSION = 1;

async function getFromIndexedDB(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);

    request.onsuccess = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(storeName)) {
        resolve(null);
        return;
      }
      const transaction = db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const getRequest = store.getAll();

      getRequest.onsuccess = () => resolve(getRequest.result);
      getRequest.onerror = () => reject(getRequest.error);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

async function deleteFromIndexedDB(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);

    request.onsuccess = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(storeName)) {
        resolve();
        return;
      }
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      store.clear();

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    };
  });
}

console.log('[SW v2] Service Worker loaded');
