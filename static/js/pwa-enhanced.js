/**
 * PWA Enhanced Features
 * Additional PWA functionality including network status, notifications, and mini-prompt
 * Version: 2.0.0
 */

(function() {
  'use strict';

  // Enhanced Configuration
  const ENHANCED_CONFIG = {
    networkStatusEnabled: true,
    floatingButtonEnabled: true,
    pushNotificationsEnabled: true,
    appBadgeEnabled: true,
    shareTargetEnabled: true,
    periodicSyncEnabled: true,
    vibrationPattern: [100, 30, 100, 30, 100],
    notificationPermissionDelay: 30000, // 30 seconds after page load
  };

  // State
  let isOnline = navigator.onLine;
  let pushSubscription = null;
  let floatingButtonElement = null;
  let networkIndicatorElement = null;

  /**
   * Initialize Enhanced PWA Features
   */
  function initEnhanced() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupEnhancedFeatures);
    } else {
      setupEnhancedFeatures();
    }
  }

  function setupEnhancedFeatures() {
    // Network status monitoring
    if (ENHANCED_CONFIG.networkStatusEnabled) {
      setupNetworkStatusMonitor();
    }

    // Floating install button
    if (ENHANCED_CONFIG.floatingButtonEnabled) {
      createFloatingInstallButton();
    }

    // Push notifications
    if (ENHANCED_CONFIG.pushNotificationsEnabled) {
      setupPushNotifications();
    }

    // App badge support
    if (ENHANCED_CONFIG.appBadgeEnabled) {
      setupAppBadge();
    }

    // Periodic background sync
    if (ENHANCED_CONFIG.periodicSyncEnabled) {
      setupPeriodicSync();
    }

    // Share target handling
    if (ENHANCED_CONFIG.shareTargetEnabled) {
      handleShareTarget();
    }

    // Enhanced styles
    injectEnhancedStyles();

    // Page visibility tracking
    setupVisibilityTracking();

    console.log('[PWA Enhanced] Features initialized');
  }

  // ==================== NETWORK STATUS MONITOR ====================

  function setupNetworkStatusMonitor() {
    createNetworkIndicator();

    window.addEventListener('online', () => {
      isOnline = true;
      updateNetworkIndicator(true);
      showNetworkToast('You\'re back online! 🌐', 'success');
      syncPendingActions();
    });

    window.addEventListener('offline', () => {
      isOnline = false;
      updateNetworkIndicator(false);
      showNetworkToast('You\'re offline. Some features may be limited.', 'warning');
    });

    // Initial state
    updateNetworkIndicator(isOnline);

    // Periodic connection check
    setInterval(checkConnectionQuality, 30000);
  }

  function createNetworkIndicator() {
    if (document.getElementById('pwa-network-indicator')) return;

    const indicator = document.createElement('div');
    indicator.id = 'pwa-network-indicator';
    indicator.className = 'pwa-network-indicator';
    indicator.innerHTML = `
      <div class="pwa-network-dot"></div>
      <span class="pwa-network-text">Online</span>
    `;
    document.body.appendChild(indicator);
    networkIndicatorElement = indicator;
  }

  function updateNetworkIndicator(online) {
    if (!networkIndicatorElement) return;

    const dot = networkIndicatorElement.querySelector('.pwa-network-dot');
    const text = networkIndicatorElement.querySelector('.pwa-network-text');

    if (online) {
      networkIndicatorElement.classList.remove('offline');
      networkIndicatorElement.classList.add('online');
      dot.style.background = '#22c55e';
      text.textContent = 'Online';
    } else {
      networkIndicatorElement.classList.remove('online');
      networkIndicatorElement.classList.add('offline');
      dot.style.background = '#ef4444';
      text.textContent = 'Offline';
    }

    // Show briefly then hide
    networkIndicatorElement.classList.add('visible');
    setTimeout(() => {
      networkIndicatorElement.classList.remove('visible');
    }, 3000);
  }

  async function checkConnectionQuality() {
    if (!navigator.connection) return;

    const connection = navigator.connection;
    const effectiveType = connection.effectiveType;
    const downlink = connection.downlink;

    // Log connection quality for analytics
    if (window.PWAInstall && typeof window.PWAInstall.logAnalytics === 'function') {
      window.PWAInstall.logAnalytics('connection_quality', {
        effectiveType,
        downlink,
        isOnline
      });
    }

    // Show slow connection warning
    if (effectiveType === '2g' || effectiveType === 'slow-2g') {
      showNetworkToast('Slow connection detected. Loading optimized content.', 'info');
    }
  }

  function showNetworkToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `pwa-network-toast ${type}`;
    toast.innerHTML = `
      <span class="pwa-toast-icon">${getToastIcon(type)}</span>
      <span class="pwa-toast-message">${message}</span>
      <button class="pwa-toast-close" aria-label="Close">×</button>
    `;

    document.body.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
      toast.classList.add('visible');
    });

    // Close button
    toast.querySelector('.pwa-toast-close').addEventListener('click', () => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 300);
    });

    // Auto remove
    setTimeout(() => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }

  function getToastIcon(type) {
    const icons = {
      success: '✓',
      warning: '⚠',
      error: '✕',
      info: 'ℹ'
    };
    return icons[type] || icons.info;
  }

  // ==================== FLOATING INSTALL BUTTON ====================

  function createFloatingInstallButton() {
    // Only show if not installed and prompt was dismissed
    const dismissed = localStorage.getItem('pwa_dismissed');
    const installed = localStorage.getItem('pwa_installed');

    if (installed === 'true') return;

    const button = document.createElement('button');
    button.id = 'pwa-floating-install';
    button.className = 'pwa-floating-install';
    button.setAttribute('aria-label', 'Install App');
    button.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <span class="pwa-fab-tooltip">Install App</span>
    `;

    document.body.appendChild(button);
    floatingButtonElement = button;

    // Show button after a delay
    setTimeout(() => {
      if (dismissed && !installed) {
        button.classList.add('visible');
      }
    }, 5000);

    // Click handler
    button.addEventListener('click', () => {
      if (window.PWAInstall && typeof window.PWAInstall.show === 'function') {
        window.PWAInstall.show();
      }
      button.classList.remove('visible');
    });

    // Listen for beforeinstallprompt
    window.addEventListener('beforeinstallprompt', () => {
      if (dismissed && !installed) {
        button.classList.add('visible');
      }
    });

    // Hide on install
    window.addEventListener('appinstalled', () => {
      button.classList.remove('visible');
      setTimeout(() => button.remove(), 300);
    });
  }

  // ==================== PUSH NOTIFICATIONS ====================

  function setupPushNotifications() {
    // Check if push is supported
    if (!('PushManager' in window)) {
      console.log('[PWA Enhanced] Push notifications not supported');
      return;
    }

    // Ask for permission after delay
    setTimeout(() => {
      checkNotificationPermission();
    }, ENHANCED_CONFIG.notificationPermissionDelay);
  }

  async function checkNotificationPermission() {
    const permission = Notification.permission;

    if (permission === 'granted') {
      await subscribeToPush();
      return;
    }

    if (permission === 'denied') {
      console.log('[PWA Enhanced] Notification permission denied');
      return;
    }

    // Show custom permission prompt
    if (shouldShowNotificationPrompt()) {
      showNotificationPermissionPrompt();
    }
  }

  function shouldShowNotificationPrompt() {
    const lastPrompt = localStorage.getItem('pwa_notification_prompt_time');
    if (!lastPrompt) return true;

    const daysSincePrompt = (Date.now() - parseInt(lastPrompt, 10)) / (1000 * 60 * 60 * 24);
    return daysSincePrompt >= 7;
  }

  function showNotificationPermissionPrompt() {
    const existing = document.getElementById('pwa-notification-prompt');
    if (existing) return;

    const prompt = document.createElement('div');
    prompt.id = 'pwa-notification-prompt';
    prompt.className = 'pwa-notification-prompt';
    prompt.innerHTML = `
      <div class="pwa-notif-icon">🔔</div>
      <div class="pwa-notif-content">
        <h4>Stay Updated</h4>
        <p>Get notified about orders, deals, and price drops!</p>
      </div>
      <div class="pwa-notif-actions">
        <button class="pwa-notif-btn pwa-notif-btn-secondary" id="pwa-notif-later">Later</button>
        <button class="pwa-notif-btn pwa-notif-btn-primary" id="pwa-notif-allow">Allow</button>
      </div>
    `;

    document.body.appendChild(prompt);

    // Animate in
    requestAnimationFrame(() => {
      prompt.classList.add('visible');
    });

    // Event handlers
    document.getElementById('pwa-notif-allow').addEventListener('click', async () => {
      prompt.classList.remove('visible');
      setTimeout(() => prompt.remove(), 300);

      const result = await Notification.requestPermission();
      if (result === 'granted') {
        await subscribeToPush();
        showNetworkToast('Notifications enabled! 🎉', 'success');
      }
    });

    document.getElementById('pwa-notif-later').addEventListener('click', () => {
      localStorage.setItem('pwa_notification_prompt_time', Date.now().toString());
      prompt.classList.remove('visible');
      setTimeout(() => prompt.remove(), 300);
    });
  }

  async function subscribeToPush() {
    try {
      const registration = await navigator.serviceWorker.ready;

      // Check for existing subscription
      pushSubscription = await registration.pushManager.getSubscription();

      if (!pushSubscription) {
        // Create new subscription
        // VAPID public key for push notifications
        // Retrieve from window.VIBE_CONFIG injected in base.html
        const vapidPublicKey = window.VIBE_CONFIG && window.VIBE_CONFIG.vapidPublicKey
          ? window.VIBE_CONFIG.vapidPublicKey
          : null;

        if (!vapidPublicKey) {
            console.warn('[PWA Enhanced] VAPID public key not found');
            return;
        }

        const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);

        pushSubscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: convertedVapidKey
        });

        // Send subscription to server
        await sendSubscriptionToServer(pushSubscription);
      }

      console.log('[PWA Enhanced] Push subscription:', pushSubscription);
    } catch (error) {
      console.error('[PWA Enhanced] Push subscription failed:', error);
    }
  }

  async function sendSubscriptionToServer(subscription) {
    try {
      await fetch('/api/push-subscription/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subscription: subscription.toJSON()
        })
      });
    } catch (error) {
      console.warn('[PWA Enhanced] Failed to send subscription to server:', error);
    }
  }

  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // ==================== APP BADGE ====================

  function setupAppBadge() {
    if (!('setAppBadge' in navigator)) return;

    // Listen for unread count updates
    window.addEventListener('pwa-badge-update', (event) => {
      const count = event.detail.count || 0;
      updateBadge(count);
    });

    // Check for unread items on load
    checkUnreadItems();
  }

  async function updateBadge(count) {
    try {
      if (count > 0) {
        await navigator.setAppBadge(count);
      } else {
        await navigator.clearAppBadge();
      }
    } catch (error) {
      console.warn('[PWA Enhanced] Badge update failed:', error);
    }
  }

  async function checkUnreadItems() {
    try {
      const response = await fetch('/api/notifications/unread-count/');
      const data = await response.json();
      if (data.count > 0) {
        updateBadge(data.count);
      }
    } catch (error) {
      // Silently fail
    }
  }

  // ==================== PERIODIC SYNC ====================

  async function setupPeriodicSync() {
    if (!('periodicSync' in navigator.serviceWorker)) return;

    try {
      const registration = await navigator.serviceWorker.ready;
      const status = await navigator.permissions.query({
        name: 'periodic-background-sync',
      });

      if (status.state === 'granted') {
        // Register for periodic sync
        await registration.periodicSync.register('content-sync', {
          minInterval: 24 * 60 * 60 * 1000, // 24 hours
        });
        console.log('[PWA Enhanced] Periodic sync registered');
      }
    } catch (error) {
      console.warn('[PWA Enhanced] Periodic sync registration failed:', error);
    }
  }

  // ==================== SHARE TARGET ====================

  function handleShareTarget() {
    if (!window.location.search.includes('share-target')) return;

    const params = new URLSearchParams(window.location.search);
    const sharedTitle = params.get('title');
    const sharedText = params.get('text');
    const sharedUrl = params.get('url');

    if (sharedTitle || sharedText || sharedUrl) {
      // Handle shared content
      console.log('[PWA Enhanced] Shared content:', { sharedTitle, sharedText, sharedUrl });

      // Dispatch event for app to handle
      window.dispatchEvent(new CustomEvent('pwa-share-received', {
        detail: { title: sharedTitle, text: sharedText, url: sharedUrl }
      }));
    }
  }

  // ==================== SYNCING PENDING ACTIONS ====================

  async function syncPendingActions() {
    const pendingActions = JSON.parse(localStorage.getItem('pwa_pending_actions') || '[]');

    if (pendingActions.length === 0) return;

    console.log('[PWA Enhanced] Syncing pending actions:', pendingActions.length);

    for (const action of pendingActions) {
      try {
        await fetch(action.url, {
          method: action.method,
          headers: action.headers,
          body: JSON.stringify(action.body)
        });
      } catch (error) {
        console.warn('[PWA Enhanced] Failed to sync action:', error);
      }
    }

    // Clear pending actions
    localStorage.removeItem('pwa_pending_actions');
    showNetworkToast('Pending changes synced successfully!', 'success');
  }

  // ==================== VISIBILITY TRACKING ====================

  function setupVisibilityTracking() {
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        // App became visible
        checkUnreadItems();
        syncPendingActions();
      } else {
        // App hidden - save any pending state
        savePendingState();
      }
    });
  }

  function savePendingState() {
    // Save any unsaved state here
    console.log('[PWA Enhanced] Saving pending state...');
  }

  // ==================== ENHANCED STYLES ====================

  function injectEnhancedStyles() {
    if (document.getElementById('pwa-enhanced-styles')) return;

    const styles = `
      <style id="pwa-enhanced-styles">
        /* Network Status Indicator */
        .pwa-network-indicator {
          position: fixed;
          top: 80px;
          right: 20px;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          background: rgba(255, 255, 255, 0.95);
          border-radius: 100px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          z-index: 99999;
          transform: translateX(150%);
          transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
          -webkit-backdrop-filter: blur(10px);
          backdrop-filter: blur(10px);
        }

        .pwa-network-indicator.visible {
          transform: translateX(0);
        }

        .pwa-network-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #22c55e;
          animation: pwa-pulse 2s infinite;
        }

        .pwa-network-indicator.offline .pwa-network-dot {
          background: #ef4444;
          animation: pwa-blink 1s infinite;
        }

        .pwa-network-text {
          font-size: 13px;
          font-weight: 500;
          color: #1e293b;
        }

        @keyframes pwa-pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.2); }
        }

        @keyframes pwa-blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }

        /* Network Toast */
        .pwa-network-toast {
          position: fixed;
          bottom: 80px;
          left: 50%;
          transform: translateX(-50%) translateY(100px);
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 20px;
          background: #1e293b;
          color: white;
          border-radius: 14px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
          z-index: 999999;
          opacity: 0;
          transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
          max-width: 90vw;
        }

        .pwa-network-toast.visible {
          transform: translateX(-50%) translateY(0);
          opacity: 1;
        }

        .pwa-network-toast.success {
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        }

        .pwa-network-toast.warning {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        .pwa-network-toast.error {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }

        .pwa-network-toast.info {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        .pwa-toast-icon {
          font-size: 18px;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
        }

        .pwa-toast-message {
          font-size: 14px;
          font-weight: 500;
          flex: 1;
        }

        .pwa-toast-close {
          background: none;
          border: none;
          color: rgba(255, 255, 255, 0.7);
          font-size: 20px;
          cursor: pointer;
          padding: 0;
          line-height: 1;
          transition: color 0.2s;
        }

        .pwa-toast-close:hover {
          color: white;
        }

        /* Floating Install Button */
        .pwa-floating-install {
          position: fixed;
          bottom: 80px;
          right: 20px;
          width: 56px;
          height: 56px;
          border-radius: 50%;
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
          color: white;
          border: none;
          cursor: pointer;
          box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);
          z-index: 99998;
          display: flex;
          align-items: center;
          justify-content: center;
          transform: scale(0);
          opacity: 0;
          transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
        }

        .pwa-floating-install.visible {
          transform: scale(1);
          opacity: 1;
        }

        .pwa-floating-install:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 30px rgba(34, 197, 94, 0.5);
        }

        .pwa-floating-install:active {
          transform: scale(0.95);
        }

        .pwa-floating-install svg {
          width: 24px;
          height: 24px;
        }

        .pwa-fab-tooltip {
          position: absolute;
          right: 70px;
          background: #1e293b;
          color: white;
          padding: 8px 14px;
          border-radius: 8px;
          font-size: 13px;
          font-weight: 500;
          white-space: nowrap;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.2s;
        }

        .pwa-fab-tooltip::after {
          content: '';
          position: absolute;
          right: -6px;
          top: 50%;
          transform: translateY(-50%);
          border: 6px solid transparent;
          border-left-color: #1e293b;
        }

        .pwa-floating-install:hover .pwa-fab-tooltip {
          opacity: 1;
        }

        /* Notification Permission Prompt */
        .pwa-notification-prompt {
          position: fixed;
          bottom: 20px;
          left: 20px;
          right: 20px;
          max-width: 380px;
          margin: 0 auto;
          background: white;
          border-radius: 20px;
          padding: 20px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
          z-index: 99999;
          display: flex;
          align-items: center;
          gap: 16px;
          transform: translateY(150%);
          opacity: 0;
          transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1);
        }

        .pwa-notification-prompt.visible {
          transform: translateY(0);
          opacity: 1;
        }

        .pwa-notif-icon {
          font-size: 32px;
          flex-shrink: 0;
        }

        .pwa-notif-content {
          flex: 1;
        }

        .pwa-notif-content h4 {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          color: #1e293b;
        }

        .pwa-notif-content p {
          margin: 0;
          font-size: 13px;
          color: #64748b;
        }

        .pwa-notif-actions {
          display: flex;
          gap: 8px;
        }

        .pwa-notif-btn {
          padding: 10px 18px;
          border-radius: 10px;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          border: none;
          transition: all 0.2s;
        }

        .pwa-notif-btn-primary {
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
          color: white;
        }

        .pwa-notif-btn-primary:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
        }

        .pwa-notif-btn-secondary {
          background: #f1f5f9;
          color: #64748b;
        }

        .pwa-notif-btn-secondary:hover {
          background: #e2e8f0;
        }

        /* Dark mode */
        @media (prefers-color-scheme: dark) {
          .pwa-network-indicator {
            background: rgba(30, 41, 59, 0.95);
          }

          .pwa-network-text {
            color: #f8fafc;
          }

          .pwa-notification-prompt {
            background: #1e293b;
          }

          .pwa-notif-content h4 {
            color: #f8fafc;
          }

          .pwa-notif-content p {
            color: #94a3b8;
          }

          .pwa-notif-btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
          }

          .pwa-notif-btn-secondary:hover {
            background: rgba(255, 255, 255, 0.15);
          }
        }

        /* Mobile responsiveness */
        @media (max-width: 480px) {
          .pwa-notification-prompt {
            flex-direction: column;
            text-align: center;
          }

          .pwa-notif-actions {
            width: 100%;
            justify-content: center;
          }

          .pwa-floating-install {
            bottom: 100px;
          }

          .pwa-network-toast {
            left: 10px;
            right: 10px;
            transform: translateX(0) translateY(100px);
          }

          .pwa-network-toast.visible {
            transform: translateX(0) translateY(0);
          }
        }

        /* Animations */
        @keyframes pwa-bounce {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        @keyframes pwa-shake {
          0%, 100% { transform: translateX(0); }
          20%, 60% { transform: translateX(-5px); }
          40%, 80% { transform: translateX(5px); }
        }

        .pwa-floating-install.attention {
          animation: pwa-bounce 0.5s ease-in-out 3;
        }
      </style>
    `;

    document.head.insertAdjacentHTML('beforeend', styles);
  }

  // ==================== PUBLIC API ====================

  window.PWAEnhanced = {
    // Network status
    isOnline: () => isOnline,
    checkConnection: checkConnectionQuality,

    // Notifications
    requestNotificationPermission: async () => {
      const result = await Notification.requestPermission();
      if (result === 'granted') {
        await subscribeToPush();
      }
      return result;
    },

    // Badge
    setBadge: updateBadge,
    clearBadge: () => updateBadge(0),

    // Floating button
    showFloatingButton: () => {
      if (floatingButtonElement) {
        floatingButtonElement.classList.add('visible');
      }
    },
    hideFloatingButton: () => {
      if (floatingButtonElement) {
        floatingButtonElement.classList.remove('visible');
      }
    },

    // Toast
    showToast: showNetworkToast,

    // Pending actions
    addPendingAction: (action) => {
      const pending = JSON.parse(localStorage.getItem('pwa_pending_actions') || '[]');
      pending.push(action);
      localStorage.setItem('pwa_pending_actions', JSON.stringify(pending));
    },

    // Force sync
    sync: syncPendingActions
  };

  // Initialize
  initEnhanced();

})();
