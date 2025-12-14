/**
 * PWA Install Prompt Manager
 * Handles install prompts, analytics, and user preferences
 * Version: 1.0.0
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    promptDelay: 3000,           // Delay before showing prompt (ms)
    snoozeTime: 24 * 60 * 60 * 1000,  // Snooze for 24 hours
    dismissTime: 7 * 24 * 60 * 60 * 1000,  // Don't show for 7 days after dismiss
    maxPromptCount: 3,           // Maximum prompts before permanent dismiss
    visitCountThreshold: 2,      // Show on nth visit
    analyticsEndpoint: '/api/pwa-analytics/',  // Analytics endpoint
    storageKeys: {
      promptCount: 'pwa_prompt_count',
      lastPrompt: 'pwa_last_prompt',
      installed: 'pwa_installed',
      dismissed: 'pwa_dismissed',
      snoozedUntil: 'pwa_snoozed_until',
      visitCount: 'pwa_visit_count',
      sessionId: 'pwa_session_id'
    }
  };

  // State
  let deferredPrompt = null;
  let isInstalled = false;
  let promptElement = null;

  /**
   * Initialize PWA Install Manager
   */
  function init() {
    // Check if already installed
    checkInstallStatus();

    // Track visit
    trackVisit();

    // Register service worker
    registerServiceWorker();

    // Listen for beforeinstallprompt
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Listen for appinstalled
    window.addEventListener('appinstalled', handleAppInstalled);

    // Check display mode
    checkDisplayMode();

    // Create and inject prompt UI
    createPromptUI();

    // Log initialization
    logAnalytics('pwa_init', {
      isInstalled,
      visitCount: getVisitCount(),
      userAgent: navigator.userAgent
    });
  }

  /**
   * Register Service Worker
   */
  async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/static/sw.js', {
          scope: '/'
        });

        console.log('[PWA] Service Worker registered:', registration.scope);

        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              showUpdateNotification();
            }
          });
        });

        logAnalytics('sw_registered', { scope: registration.scope });
      } catch (error) {
        console.error('[PWA] Service Worker registration failed:', error);
        logAnalytics('sw_registration_failed', { error: error.message });
      }
    }
  }

  /**
   * Handle beforeinstallprompt event
   */
  function handleBeforeInstallPrompt(event) {
    console.log('[PWA] beforeinstallprompt fired');

    // Prevent Chrome's default prompt
    event.preventDefault();

    // Store the event for later use
    deferredPrompt = event;

    logAnalytics('install_prompt_available', {
      platforms: event.platforms || []
    });

    // Check if we should show prompt
    if (shouldShowPrompt()) {
      setTimeout(() => showInstallPrompt(), CONFIG.promptDelay);
    }
  }

  /**
   * Handle appinstalled event
   */
  function handleAppInstalled(event) {
    console.log('[PWA] App installed');

    isInstalled = true;
    localStorage.setItem(CONFIG.storageKeys.installed, 'true');

    hidePrompt();

    // Show success message
    showToast('🎉 AGRI B2B installed successfully!', 'success');

    logAnalytics('pwa_installed', {
      timestamp: Date.now(),
      source: 'native_prompt'
    });
  }

  /**
   * Check if app is already installed
   */
  function checkInstallStatus() {
    // Check localStorage flag
    if (localStorage.getItem(CONFIG.storageKeys.installed) === 'true') {
      isInstalled = true;
      return;
    }

    // Check display mode
    if (window.matchMedia('(display-mode: standalone)').matches ||
        window.matchMedia('(display-mode: fullscreen)').matches ||
        window.matchMedia('(display-mode: minimal-ui)').matches) {
      isInstalled = true;
      localStorage.setItem(CONFIG.storageKeys.installed, 'true');
      return;
    }

    // Check iOS standalone mode
    if (window.navigator.standalone === true) {
      isInstalled = true;
      localStorage.setItem(CONFIG.storageKeys.installed, 'true');
      return;
    }
  }

  /**
   * Check display mode for PWA
   */
  function checkDisplayMode() {
    const mqStandalone = window.matchMedia('(display-mode: standalone)');

    mqStandalone.addEventListener('change', (event) => {
      if (event.matches) {
        isInstalled = true;
        localStorage.setItem(CONFIG.storageKeys.installed, 'true');
        logAnalytics('pwa_launched_standalone', {});
      }
    });
  }

  /**
   * Track user visit
   */
  function trackVisit() {
    const visitCount = getVisitCount() + 1;
    localStorage.setItem(CONFIG.storageKeys.visitCount, visitCount.toString());

    // Generate session ID if not exists
    if (!sessionStorage.getItem(CONFIG.storageKeys.sessionId)) {
      sessionStorage.setItem(CONFIG.storageKeys.sessionId, generateSessionId());
    }

    logAnalytics('page_visit', { visitCount });
  }

  /**
   * Get visit count
   */
  function getVisitCount() {
    return parseInt(localStorage.getItem(CONFIG.storageKeys.visitCount) || '0', 10);
  }

  /**
   * Determine if prompt should be shown
   */
  function shouldShowPrompt() {
    // Don't show if already installed
    if (isInstalled) {
      return false;
    }

    // Don't show if no deferred prompt
    if (!deferredPrompt && !isIOSDevice()) {
      return false;
    }

    // Check if permanently dismissed
    const dismissed = localStorage.getItem(CONFIG.storageKeys.dismissed);
    if (dismissed === 'permanent') {
      return false;
    }

    // Check dismiss timeout
    if (dismissed) {
      const dismissedTime = parseInt(dismissed, 10);
      if (Date.now() < dismissedTime + CONFIG.dismissTime) {
        return false;
      }
    }

    // Check if snoozed
    const snoozedUntil = localStorage.getItem(CONFIG.storageKeys.snoozedUntil);
    if (snoozedUntil && Date.now() < parseInt(snoozedUntil, 10)) {
      return false;
    }

    // Check prompt count
    const promptCount = parseInt(localStorage.getItem(CONFIG.storageKeys.promptCount) || '0', 10);
    if (promptCount >= CONFIG.maxPromptCount) {
      return false;
    }

    // Check visit threshold
    if (getVisitCount() < CONFIG.visitCountThreshold) {
      return false;
    }

    return true;
  }

  /**
   * Check if iOS device
   */
  function isIOSDevice() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }

  /**
   * Check if Safari browser
   */
  function isSafari() {
    return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  }

  /**
   * Create prompt UI
   */
  function createPromptUI() {
    // Don't create if already exists
    if (document.getElementById('pwa-install-prompt')) {
      return;
    }

    const html = `
      <div id="pwa-install-prompt" class="pwa-prompt" role="dialog" aria-labelledby="pwa-prompt-title" aria-modal="true">
        <div class="pwa-prompt-backdrop"></div>
        <div class="pwa-prompt-container">
          <div class="pwa-prompt-header">
            <div class="pwa-prompt-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="24" cy="24" r="24" fill="url(#gradient1)"/>
                <path d="M24 12C22.9 12 22 12.9 22 14V24H14C12.9 24 12 24.9 12 26C12 27.1 12.9 28 14 28H22V34C22 35.1 22.9 36 24 36C25.1 36 26 35.1 26 34V28H34C35.1 28 36 27.1 36 26C36 24.9 35.1 24 34 24H26V14C26 12.9 25.1 12 24 12Z" fill="white"/>
                <defs>
                  <linearGradient id="gradient1" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#22c55e"/>
                    <stop offset="1" stop-color="#16a34a"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <button class="pwa-prompt-close" id="pwa-close-btn" aria-label="Close">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <div class="pwa-prompt-content">
            <h2 id="pwa-prompt-title" class="pwa-prompt-title">Install AGRI B2B</h2>
            <p class="pwa-prompt-description">
              Get the full app experience! Install AGRI B2B on your device for faster access, offline browsing, and exclusive features.
            </p>

            <div class="pwa-prompt-features">
              <div class="pwa-feature">
                <span class="pwa-feature-icon">⚡</span>
                <span class="pwa-feature-text">Faster loading</span>
              </div>
              <div class="pwa-feature">
                <span class="pwa-feature-icon">📱</span>
                <span class="pwa-feature-text">Works offline</span>
              </div>
              <div class="pwa-feature">
                <span class="pwa-feature-icon">🔔</span>
                <span class="pwa-feature-text">Push notifications</span>
              </div>
            </div>

            <div class="pwa-prompt-instructions" id="pwa-ios-instructions" style="display: none;">
              <p class="pwa-instructions-title">To install on iOS:</p>
              <ol class="pwa-instructions-list">
                <li>Tap the <strong>Share</strong> button <span class="pwa-share-icon">⬆️</span></li>
                <li>Scroll down and tap <strong>"Add to Home Screen"</strong></li>
                <li>Tap <strong>"Add"</strong> to confirm</li>
              </ol>
            </div>
          </div>

          <div class="pwa-prompt-actions">
            <button class="pwa-btn pwa-btn-secondary" id="pwa-snooze-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              Remind me later
            </button>
            <button class="pwa-btn pwa-btn-primary" id="pwa-install-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              Install App
            </button>
          </div>

          <div class="pwa-prompt-footer">
            <button class="pwa-link" id="pwa-dismiss-btn">Don't show again</button>
          </div>
        </div>
      </div>
    `;

    // Inject CSS
    injectStyles();

    // Create element
    const container = document.createElement('div');
    container.innerHTML = html;
    document.body.appendChild(container.firstElementChild);

    promptElement = document.getElementById('pwa-install-prompt');

    // Add event listeners
    setupEventListeners();
  }

  /**
   * Inject PWA prompt styles
   */
  function injectStyles() {
    if (document.getElementById('pwa-styles')) {
      return;
    }

    const styles = `
      <style id="pwa-styles">
        .pwa-prompt {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 999999;
          display: flex;
          align-items: flex-end;
          justify-content: center;
          opacity: 0;
          visibility: hidden;
          transition: opacity 0.3s ease, visibility 0.3s ease;
        }

        .pwa-prompt.active {
          opacity: 1;
          visibility: visible;
        }

        .pwa-prompt-backdrop {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          -webkit-backdrop-filter: blur(4px);
          backdrop-filter: blur(4px);
        }

        .pwa-prompt-container {
          position: relative;
          width: 100%;
          max-width: 420px;
          background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
          border-radius: 24px 24px 0 0;
          box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.15);
          padding: 24px;
          transform: translateY(100%);
          transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1);
          max-height: 90vh;
          overflow-y: auto;
        }

        .pwa-prompt.active .pwa-prompt-container {
          transform: translateY(0);
        }

        @media (min-width: 640px) {
          .pwa-prompt {
            align-items: center;
          }

          .pwa-prompt-container {
            border-radius: 24px;
            margin: 20px;
            transform: scale(0.95) translateY(20px);
          }

          .pwa-prompt.active .pwa-prompt-container {
            transform: scale(1) translateY(0);
          }
        }

        .pwa-prompt-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          margin-bottom: 16px;
        }

        .pwa-prompt-icon {
          width: 56px;
          height: 56px;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
        }

        .pwa-prompt-icon svg {
          width: 100%;
          height: 100%;
        }

        .pwa-prompt-close {
          width: 36px;
          height: 36px;
          border: none;
          background: rgba(0, 0, 0, 0.05);
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #64748b;
          transition: all 0.2s ease;
        }

        .pwa-prompt-close:hover {
          background: rgba(0, 0, 0, 0.1);
          color: #1e293b;
        }

        .pwa-prompt-content {
          margin-bottom: 24px;
        }

        .pwa-prompt-title {
          font-size: 24px;
          font-weight: 700;
          color: #1e293b;
          margin: 0 0 8px 0;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .pwa-prompt-description {
          font-size: 15px;
          color: #64748b;
          line-height: 1.6;
          margin: 0 0 20px 0;
        }

        .pwa-prompt-features {
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
        }

        .pwa-feature {
          display: flex;
          align-items: center;
          gap: 6px;
          background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
          padding: 8px 14px;
          border-radius: 100px;
          font-size: 13px;
          color: #166534;
          font-weight: 500;
        }

        .pwa-feature-icon {
          font-size: 14px;
        }

        .pwa-prompt-instructions {
          margin-top: 20px;
          padding: 16px;
          background: #f8fafc;
          border-radius: 16px;
          border: 1px solid #e2e8f0;
        }

        .pwa-instructions-title {
          font-size: 14px;
          font-weight: 600;
          color: #1e293b;
          margin: 0 0 12px 0;
        }

        .pwa-instructions-list {
          margin: 0;
          padding-left: 20px;
          font-size: 14px;
          color: #64748b;
          line-height: 1.8;
        }

        .pwa-instructions-list li {
          margin-bottom: 4px;
        }

        .pwa-share-icon {
          display: inline-block;
          font-size: 16px;
        }

        .pwa-prompt-actions {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .pwa-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 14px 20px;
          border-radius: 14px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          border: none;
          transition: all 0.2s ease;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .pwa-btn-primary {
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
          color: white;
          box-shadow: 0 4px 14px rgba(34, 197, 94, 0.4);
        }

        .pwa-btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(34, 197, 94, 0.5);
        }

        .pwa-btn-primary:active {
          transform: translateY(0);
        }

        .pwa-btn-secondary {
          background: #f1f5f9;
          color: #475569;
        }

        .pwa-btn-secondary:hover {
          background: #e2e8f0;
        }

        .pwa-prompt-footer {
          text-align: center;
        }

        .pwa-link {
          background: none;
          border: none;
          color: #94a3b8;
          font-size: 13px;
          cursor: pointer;
          padding: 8px 16px;
          transition: color 0.2s ease;
        }

        .pwa-link:hover {
          color: #64748b;
          text-decoration: underline;
        }

        /* Toast notification */
        .pwa-toast {
          position: fixed;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%) translateY(100px);
          background: #1e293b;
          color: white;
          padding: 14px 24px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 500;
          z-index: 1000000;
          opacity: 0;
          transition: all 0.3s ease;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .pwa-toast.active {
          transform: translateX(-50%) translateY(0);
          opacity: 1;
        }

        .pwa-toast.success {
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        }

        /* Update notification banner */
        .pwa-update-banner {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          color: white;
          padding: 12px 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 16px;
          z-index: 999998;
          transform: translateY(-100%);
          transition: transform 0.3s ease;
        }

        .pwa-update-banner.active {
          transform: translateY(0);
        }

        .pwa-update-banner button {
          background: white;
          color: #2563eb;
          border: none;
          padding: 8px 16px;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          font-size: 13px;
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
          .pwa-prompt-container {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
          }

          .pwa-prompt-title {
            color: #f8fafc;
          }

          .pwa-prompt-description {
            color: #94a3b8;
          }

          .pwa-prompt-close {
            background: rgba(255, 255, 255, 0.1);
            color: #94a3b8;
          }

          .pwa-prompt-close:hover {
            background: rgba(255, 255, 255, 0.2);
            color: #f8fafc;
          }

          .pwa-feature {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.2) 100%);
            color: #4ade80;
          }

          .pwa-prompt-instructions {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.1);
          }

          .pwa-instructions-title {
            color: #f8fafc;
          }

          .pwa-instructions-list {
            color: #94a3b8;
          }

          .pwa-btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
          }

          .pwa-btn-secondary:hover {
            background: rgba(255, 255, 255, 0.15);
          }

          .pwa-link {
            color: #64748b;
          }

          .pwa-link:hover {
            color: #94a3b8;
          }
        }
      </style>
    `;

    document.head.insertAdjacentHTML('beforeend', styles);
  }

  /**
   * Setup event listeners for prompt
   */
  function setupEventListeners() {
    const installBtn = document.getElementById('pwa-install-btn');
    const snoozeBtn = document.getElementById('pwa-snooze-btn');
    const dismissBtn = document.getElementById('pwa-dismiss-btn');
    const closeBtn = document.getElementById('pwa-close-btn');
    const backdrop = promptElement.querySelector('.pwa-prompt-backdrop');

    installBtn.addEventListener('click', handleInstallClick);
    snoozeBtn.addEventListener('click', handleSnoozeClick);
    dismissBtn.addEventListener('click', handleDismissClick);
    closeBtn.addEventListener('click', handleCloseClick);
    backdrop.addEventListener('click', handleCloseClick);

    // Keyboard accessibility
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && promptElement.classList.contains('active')) {
        handleCloseClick();
      }
    });
  }

  /**
   * Show install prompt
   */
  function showInstallPrompt() {
    if (!promptElement || isInstalled) {
      return;
    }

    // Increment prompt count
    const promptCount = parseInt(localStorage.getItem(CONFIG.storageKeys.promptCount) || '0', 10);
    localStorage.setItem(CONFIG.storageKeys.promptCount, (promptCount + 1).toString());
    localStorage.setItem(CONFIG.storageKeys.lastPrompt, Date.now().toString());

    // Show iOS instructions if needed
    if (isIOSDevice()) {
      document.getElementById('pwa-ios-instructions').style.display = 'block';
      document.getElementById('pwa-install-btn').textContent = 'Got it!';
    }

    // Show prompt with animation
    promptElement.classList.add('active');

    // Focus trap for accessibility
    const firstFocusable = promptElement.querySelector('button');
    if (firstFocusable) {
      firstFocusable.focus();
    }

    logAnalytics('prompt_shown', {
      promptCount: promptCount + 1,
      isIOS: isIOSDevice(),
      deviceType: getDeviceType()
    });
  }

  /**
   * Hide prompt
   */
  function hidePrompt() {
    if (promptElement) {
      promptElement.classList.remove('active');
    }
  }

  /**
   * Handle install button click
   */
  async function handleInstallClick() {
    logAnalytics('install_clicked', {});

    if (isIOSDevice()) {
      // For iOS, just hide the prompt (user follows manual instructions)
      hidePrompt();
      showToast('Follow the instructions to add to home screen', 'info');
      return;
    }

    if (!deferredPrompt) {
      console.warn('[PWA] No deferred prompt available');
      showToast('Installation not available. Please try again later.', 'error');
      return;
    }

    try {
      // Show the native install prompt
      deferredPrompt.prompt();

      // Wait for user response
      const { outcome } = await deferredPrompt.userChoice;

      logAnalytics('install_prompt_result', {
        outcome,
        timestamp: Date.now()
      });

      if (outcome === 'accepted') {
        console.log('[PWA] User accepted install prompt');
        isInstalled = true;
        localStorage.setItem(CONFIG.storageKeys.installed, 'true');
      } else {
        console.log('[PWA] User dismissed install prompt');
      }

      // Clear the deferred prompt
      deferredPrompt = null;
      hidePrompt();

    } catch (error) {
      console.error('[PWA] Install prompt error:', error);
      logAnalytics('install_prompt_error', { error: error.message });
    }
  }

  /**
   * Handle snooze button click
   */
  function handleSnoozeClick() {
    const snoozedUntil = Date.now() + CONFIG.snoozeTime;
    localStorage.setItem(CONFIG.storageKeys.snoozedUntil, snoozedUntil.toString());

    hidePrompt();
    showToast('We\'ll remind you later!', 'info');

    logAnalytics('prompt_snoozed', {
      snoozedUntil,
      duration: CONFIG.snoozeTime
    });
  }

  /**
   * Handle dismiss button click
   */
  function handleDismissClick() {
    const promptCount = parseInt(localStorage.getItem(CONFIG.storageKeys.promptCount) || '0', 10);

    if (promptCount >= CONFIG.maxPromptCount - 1) {
      // Permanent dismiss after max prompts
      localStorage.setItem(CONFIG.storageKeys.dismissed, 'permanent');
    } else {
      // Temporary dismiss
      localStorage.setItem(CONFIG.storageKeys.dismissed, Date.now().toString());
    }

    hidePrompt();

    logAnalytics('prompt_dismissed', {
      promptCount,
      permanent: promptCount >= CONFIG.maxPromptCount - 1
    });
  }

  /**
   * Handle close button click
   */
  function handleCloseClick() {
    hidePrompt();
    logAnalytics('prompt_closed', {});
  }

  /**
   * Show update notification
   */
  function showUpdateNotification() {
    const banner = document.createElement('div');
    banner.className = 'pwa-update-banner';
    banner.innerHTML = `
      <span>🚀 A new version is available!</span>
      <button id="pwa-update-btn">Update Now</button>
    `;

    document.body.appendChild(banner);

    setTimeout(() => banner.classList.add('active'), 100);

    document.getElementById('pwa-update-btn').addEventListener('click', () => {
      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
      }
      window.location.reload();
    });

    logAnalytics('update_available', {});
  }

  /**
   * Show toast notification
   */
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `pwa-toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('active'), 100);

    setTimeout(() => {
      toast.classList.remove('active');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  /**
   * Log analytics event
   */
  function logAnalytics(eventName, data) {
    const payload = {
      event: eventName,
      data: {
        ...data,
        timestamp: new Date().toISOString(),
        sessionId: sessionStorage.getItem(CONFIG.storageKeys.sessionId),
        url: window.location.href,
        referrer: document.referrer
      }
    };

    // Log to console in development
    console.log('[PWA Analytics]', payload);

    // Send to analytics endpoint (if available)
    if (navigator.sendBeacon && CONFIG.analyticsEndpoint) {
      try {
        navigator.sendBeacon(
          CONFIG.analyticsEndpoint,
          JSON.stringify(payload)
        );
      } catch (error) {
        // Silently fail - analytics shouldn't break the app
      }
    }

    // Also store locally for later sync
    storeAnalyticsLocally(payload);
  }

  /**
   * Store analytics locally for offline sync
   */
  function storeAnalyticsLocally(payload) {
    try {
      const stored = JSON.parse(localStorage.getItem('pwa_analytics_queue') || '[]');
      stored.push(payload);

      // Keep only last 100 events
      while (stored.length > 100) {
        stored.shift();
      }

      localStorage.setItem('pwa_analytics_queue', JSON.stringify(stored));
    } catch (error) {
      // Storage might be full, silently fail
    }
  }

  /**
   * Generate unique session ID
   */
  function generateSessionId() {
    return 'pwa_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Get device type
   */
  function getDeviceType() {
    const ua = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(ua)) {
      return 'tablet';
    }
    if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(ua)) {
      return 'mobile';
    }
    return 'desktop';
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose API for external use
  window.PWAInstall = {
    show: showInstallPrompt,
    hide: hidePrompt,
    isInstalled: () => isInstalled,
    canInstall: () => !!deferredPrompt || isIOSDevice()
  };

})();
