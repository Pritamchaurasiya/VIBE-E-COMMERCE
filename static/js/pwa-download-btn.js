/**
 * PWA Download Button Manager
 * Premium Download App button with stunning animations and effects
 * Version: 2.0.0
 */

(function() {
  'use strict';

  // State
  let deferredPrompt = null;
  let isInstalled = false;
  let downloadBtnElement = null;
  let promptModalElement = null;

  /**
   * Initialize Download Button
   */
  function init() {
    // Wait for DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setup);
    } else {
      setup();
    }
  }

  function setup() {
    // Check if already installed
    checkInstallStatus();

    // Create download button in navbar
    createNavbarDownloadButton();

    // Create enhanced prompt modal
    createEnhancedPromptModal();

    // Create download banner if on homepage
    if (isHomepage()) {
      createDownloadBanner();
    }

    // Listen for install events
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Show/hide based on install status
    updateButtonVisibility();

    console.log('[PWA Download] Initialized');
  }

  /**
   * Check if app is installed
   */
  function checkInstallStatus() {
    if (localStorage.getItem('pwa_installed') === 'true') {
      isInstalled = true;
      document.body.classList.add('pwa-installed');
      return;
    }

    if (window.matchMedia('(display-mode: standalone)').matches ||
        window.matchMedia('(display-mode: fullscreen)').matches ||
        window.navigator.standalone === true) {
      isInstalled = true;
      document.body.classList.add('pwa-installed', 'standalone-mode');
    }
  }

  /**
   * Check if on homepage
   */
  function isHomepage() {
    return window.location.pathname === '/' || window.location.pathname === '/frontpage/';
  }

  /**
   * Handle beforeinstallprompt
   */
  function handleBeforeInstallPrompt(event) {
    event.preventDefault();
    deferredPrompt = event;
    updateButtonVisibility();
    console.log('[PWA Download] Install prompt available');
  }

  /**
   * Handle app installed
   */
  function handleAppInstalled() {
    isInstalled = true;
    localStorage.setItem('pwa_installed', 'true');
    document.body.classList.add('pwa-installed');
    hidePromptModal();
    showSuccessAnimation();
    updateButtonVisibility();
    console.log('[PWA Download] App installed!');
  }

  /**
   * Update button visibility
   */
  function updateButtonVisibility() {
    const buttons = document.querySelectorAll('.download-app-btn, .pwa-download-large-btn');
    buttons.forEach(btn => {
      if (isInstalled) {
        btn.style.display = 'none';
      } else {
        btn.style.display = '';
      }
    });

    // Hide banner if installed
    const banner = document.querySelector('.pwa-download-banner');
    if (banner && isInstalled) {
      banner.style.display = 'none';
    }
  }

  /**
   * Create navbar download button
   */
  function createNavbarDownloadButton() {
    // Find the navbar actions area
    const navbarActions = document.querySelector('.navbar .d-flex.align-items-center');
    if (!navbarActions || document.querySelector('.download-app-btn')) return;

    const button = document.createElement('button');
    button.className = 'download-app-btn me-3';
    button.id = 'navbar-download-btn';
    button.innerHTML = `
      <span class="btn-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </span>
      <span class="btn-text">Download App</span>
      <span class="btn-badge">NEW</span>
    `;

    button.addEventListener('click', showPromptModal);

    // Insert before dark mode toggle
    const darkModeBtn = navbarActions.querySelector('#darkModeToggle');
    if (darkModeBtn) {
      navbarActions.insertBefore(button, darkModeBtn);
    } else {
      navbarActions.prepend(button);
    }

    downloadBtnElement = button;

    // Add ripple effect on click
    button.addEventListener('click', createRipple);
  }

  /**
   * Create ripple effect
   */
  function createRipple(event) {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.classList.add('ripple-effect');

    const ripple = button.querySelector('.ripple-effect');
    if (ripple) ripple.remove();

    button.appendChild(circle);
  }

  /**
   * Create enhanced prompt modal
   */
  function createEnhancedPromptModal() {
    if (document.getElementById('pwa-prompt-v2')) return;

    const modal = document.createElement('div');
    modal.id = 'pwa-prompt-v2';
    modal.className = 'pwa-prompt-v2';
    modal.innerHTML = `
      <div class="prompt-backdrop"></div>
      <div class="prompt-card">
        <button class="prompt-close" aria-label="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>

        <div class="prompt-icon-container">
          <div class="prompt-icon">🌱</div>
        </div>

        <h2 class="prompt-title">Get AGRI B2B App</h2>
        <p class="prompt-subtitle">Install our app for the best experience with faster loading, offline access, and instant notifications!</p>

        <div class="prompt-features">
          <div class="prompt-feature-item">
            <span class="feature-emoji">⚡</span>
            <span class="feature-label">Lightning Fast</span>
          </div>
          <div class="prompt-feature-item">
            <span class="feature-emoji">📶</span>
            <span class="feature-label">Works Offline</span>
          </div>
          <div class="prompt-feature-item">
            <span class="feature-emoji">🔔</span>
            <span class="feature-label">Notifications</span>
          </div>
        </div>

        <div class="prompt-actions">
          <button class="prompt-install-btn" id="prompt-install-btn">
            <span class="install-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </span>
            Install Now — It's Free!
          </button>

          <div class="prompt-secondary-actions">
            <button class="prompt-secondary-btn" id="prompt-later-btn">
              <span>⏰</span> Remind Later
            </button>
            <button class="prompt-secondary-btn" id="prompt-dismiss-btn">
              <span>✕</span> Not Now
            </button>
          </div>
        </div>

        <div id="ios-instructions" style="display: none; margin-top: 20px; text-align: center;">
          <p style="font-size: 14px; color: #64748b; margin-bottom: 12px;">To install on iOS:</p>
          <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;">
            <span style="background: #f1f5f9; padding: 8px 16px; border-radius: 100px; font-size: 13px;">1. Tap <strong>⬆️ Share</strong></span>
            <span style="background: #f1f5f9; padding: 8px 16px; border-radius: 100px; font-size: 13px;">2. <strong>Add to Home Screen</strong></span>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    promptModalElement = modal;

    // Event listeners
    modal.querySelector('.prompt-backdrop').addEventListener('click', hidePromptModal);
    modal.querySelector('.prompt-close').addEventListener('click', hidePromptModal);
    modal.querySelector('#prompt-install-btn').addEventListener('click', triggerInstall);
    modal.querySelector('#prompt-later-btn').addEventListener('click', handleLater);
    modal.querySelector('#prompt-dismiss-btn').addEventListener('click', handleDismiss);

    // Keyboard escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('active')) {
        hidePromptModal();
      }
    });

    // Show iOS instructions if needed
    if (isIOSDevice()) {
      modal.querySelector('#ios-instructions').style.display = 'block';
      modal.querySelector('#prompt-install-btn').textContent = 'Got it!';
    }
  }

  /**
   * Check if iOS
   */
  function isIOSDevice() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }

  /**
   * Show prompt modal
   */
  function showPromptModal() {
    if (!promptModalElement || isInstalled) return;
    promptModalElement.classList.add('active');
    document.body.style.overflow = 'hidden';
    logAnalytics('prompt_shown');
  }

  /**
   * Hide prompt modal
   */
  function hidePromptModal() {
    if (!promptModalElement) return;
    promptModalElement.classList.remove('active');
    document.body.style.overflow = '';
  }

  /**
   * Trigger install
   */
  async function triggerInstall() {
    if (isIOSDevice()) {
      hidePromptModal();
      return;
    }

    if (!deferredPrompt) {
      console.log('[PWA Download] No deferred prompt available');
      hidePromptModal();
      return;
    }

    logAnalytics('install_clicked');

    try {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        console.log('[PWA Download] User accepted install');
        logAnalytics('install_accepted');
      } else {
        console.log('[PWA Download] User dismissed install');
        logAnalytics('install_dismissed');
      }
    } catch (error) {
      console.error('[PWA Download] Install error:', error);
    }

    deferredPrompt = null;
    hidePromptModal();
  }

  /**
   * Handle later
   */
  function handleLater() {
    localStorage.setItem('pwa_snoozed_until', (Date.now() + 24 * 60 * 60 * 1000).toString());
    hidePromptModal();
    logAnalytics('prompt_snoozed');
  }

  /**
   * Handle dismiss
   */
  function handleDismiss() {
    hidePromptModal();
    logAnalytics('prompt_closed');
  }

  /**
   * Show success animation
   */
  function showSuccessAnimation() {
    const overlay = document.createElement('div');
    overlay.className = 'install-success-overlay';
    overlay.innerHTML = `
      <div class="success-checkmark">
        <svg viewBox="0 0 52 52">
          <circle cx="26" cy="26" r="25" fill="none" stroke="#22c55e" stroke-width="2"/>
          <path fill="none" stroke="#22c55e" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
        </svg>
      </div>
      <h2 class="success-title">App Installed!</h2>
      <p class="success-subtitle">AGRI B2B is now on your device</p>
    `;

    document.body.appendChild(overlay);

    // Create confetti
    createConfetti(overlay);

    // Animate in
    requestAnimationFrame(() => {
      overlay.classList.add('active');
    });

    // Remove after delay
    setTimeout(() => {
      overlay.classList.remove('active');
      setTimeout(() => overlay.remove(), 500);
    }, 3000);
  }

  /**
   * Create confetti effect
   */
  function createConfetti(container) {
    const colors = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#a855f7', '#ec4899'];

    for (let i = 0; i < 50; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti';
      confetti.style.left = Math.random() * 100 + '%';
      confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
      confetti.style.animationDelay = Math.random() * 0.5 + 's';
      confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
      container.appendChild(confetti);
    }
  }

  /**
   * Create download banner for homepage
   */
  function createDownloadBanner() {
    if (isInstalled || document.querySelector('.pwa-download-banner')) return;

    const mainContent = document.querySelector('main') || document.querySelector('.container');
    if (!mainContent) return;

    const banner = document.createElement('section');
    banner.className = 'pwa-download-banner';
    banner.innerHTML = `
      <div class="pwa-particles">
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
        <div class="pwa-particle"></div>
      </div>

      <div class="pwa-banner-content">
        <div class="pwa-banner-text">
          <h2 class="pwa-banner-title">📱 Download Our App</h2>
          <p class="pwa-banner-subtitle">
            Get the full AGRI B2B experience! Install our app for lightning-fast performance, offline access, and exclusive deals.
          </p>

          <div class="pwa-banner-features">
            <div class="pwa-banner-feature">
              <span class="feature-icon">⚡</span>
              <span>3x Faster</span>
            </div>
            <div class="pwa-banner-feature">
              <span class="feature-icon">📶</span>
              <span>Works Offline</span>
            </div>
            <div class="pwa-banner-feature">
              <span class="feature-icon">🔔</span>
              <span>Push Notifications</span>
            </div>
            <div class="pwa-banner-feature">
              <span class="feature-icon">💾</span>
              <span>Saves Data</span>
            </div>
          </div>

          <button class="pwa-download-large-btn" id="banner-download-btn">
            <span class="btn-icon-large">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </span>
            <span class="btn-content">
              <span class="btn-label">Free Download</span>
              <span class="btn-main-text">Get the App Now</span>
            </span>
          </button>
        </div>

        <div class="pwa-banner-mockup">
          <div class="phone-frame">
            <div class="phone-notch"></div>
            <div class="phone-screen">
              <div class="phone-app-icon">🌾</div>
              <span class="phone-app-name">AGRI B2B</span>
            </div>
          </div>
        </div>
      </div>
    `;

    // Insert at the beginning of main content
    mainContent.insertBefore(banner, mainContent.firstChild);

    // Add click handler
    banner.querySelector('#banner-download-btn').addEventListener('click', showPromptModal);
  }

  /**
   * Log analytics
   */
  function logAnalytics(event, data = {}) {
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/pwa-analytics/', JSON.stringify({
          event,
          data: {
            ...data,
            timestamp: Date.now(),
            url: window.location.href
          }
        }));
      }
    } catch (error) {
      console.warn('[PWA Download] Analytics error:', error);
    }
  }

  // Add ripple effect styles
  const rippleStyles = document.createElement('style');
  rippleStyles.textContent = `
    .ripple-effect {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.4);
      transform: scale(0);
      animation: ripple-animation 0.6s ease-out;
      pointer-events: none;
    }

    @keyframes ripple-animation {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(rippleStyles);

  // Expose API
  window.PWADownload = {
    showPrompt: showPromptModal,
    hidePrompt: hidePromptModal,
    isInstalled: () => isInstalled,
    canInstall: () => !!deferredPrompt
  };

  // Initialize
  init();

})();
