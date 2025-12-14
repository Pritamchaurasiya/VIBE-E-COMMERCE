import { createSlice } from '@reduxjs/toolkit';

/**
 * Theme slice state interface
 * @typedef {Object} ThemeState
 * @property {'light'|'dark'} currentTheme - Current active theme
 * @property {boolean} prefersSystem - Whether to use system preference
 * @property {boolean} isSystemSynced - Whether theme is synced with system
 * @property {boolean} isTransitioning - Whether theme transition is in progress
 * @property {boolean} persistPreference - Whether to persist user preference
 * @property {string} systemTheme - Detected system theme preference
 * @property {string} error - Any error message
 */

/**
 * Initial state for theme slice
 * @type {ThemeState}
 */
const initialState = {
  currentTheme: 'light',
  prefersSystem: false,
  isSystemSynced: false,
  isTransitioning: false,
  persistPreference: true,
  systemTheme: window.matchMedia?.('(prefers-color-scheme: dark)')?.matches ? 'dark' : 'light',
  error: null,
};

/**
 * Helper function to safely access localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key doesn't exist
 * @returns {any} Stored value or default
 */
const safeGetLocalStorage = (key, defaultValue) => {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : defaultValue;
  } catch (error) {
    console.warn(`LocalStorage read failed for ${key}:`, error);
    return defaultValue;
  }
};

/**
 * Helper function to safely set localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 * @returns {boolean} Success status
 */
const safeSetLocalStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`LocalStorage write failed for ${key}:`, error);
    return false;
  }
};

/**
 * Helper function to sync CSS variables with current theme
 * @param {'light'|'dark'} theme - Theme to apply
 */
const syncCSSVariables = (theme) => {
  const root = document.documentElement;
  if (!root) return;

  // Define theme-specific CSS variables
  const themeVars = {
    light: {
      '--color-background': '#ffffff',
      '--color-text': '#333333',
      '--color-primary': '#4a6bff',
      '--color-secondary': '#f5f5f5',
      '--color-border': '#e0e0e0',
      '--color-shadow': 'rgba(0, 0, 0, 0.1)',
    },
    dark: {
      '--color-background': '#1a1a1a',
      '--color-text': '#f0f0f0',
      '--color-primary': '#6a8bff',
      '--color-secondary': '#2a2a2a',
      '--color-border': '#404040',
      '--color-shadow': 'rgba(0, 0, 0, 0.3)',
    }
  };

  // Apply theme variables
  Object.entries(themeVars[theme]).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });

  // Add/remove dark class for additional styling
  root.classList.toggle('dark-theme', theme === 'dark');
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    /**
     * Toggle between light and dark themes with smooth transition
     * @param {ThemeState} state
     */
    toggleTheme: (state) => {
      if (state.isTransitioning) return; // Prevent rapid toggling

      const newTheme = state.currentTheme === 'light' ? 'dark' : 'light';
      state.currentTheme = newTheme;
      state.isTransitioning = true;
      state.error = null;

      // Sync with CSS
      syncCSSVariables(newTheme);

      // Persist if enabled
      if (state.persistPreference) {
        safeSetLocalStorage('themePreference', {
          theme: newTheme,
          prefersSystem: state.prefersSystem
        });
      }
    },

    /**
     * Force set a specific theme
     * @param {ThemeState} state
     * @param {{payload: 'light'|'dark'}} action
     */
    setTheme: (state, action) => {
      const theme = action.payload;
      if (theme !== 'light' && theme !== 'dark') {
        state.error = 'Invalid theme specified';
        return;
      }

      state.currentTheme = theme;
      state.isTransitioning = false;
      state.error = null;

      // Sync with CSS
      syncCSSVariables(theme);

      // Persist if enabled
      if (state.persistPreference) {
        safeSetLocalStorage('themePreference', {
          theme,
          prefersSystem: state.prefersSystem
        });
      }
    },

    /**
     * Update persistence settings
     * @param {ThemeState} state
     * @param {{payload: boolean}} action
     */
    setPreference: (state, action) => {
      state.persistPreference = action.payload;

      // If enabling persistence, save current state
      if (action.payload) {
        safeSetLocalStorage('themePreference', {
          theme: state.currentTheme,
          prefersSystem: state.prefersSystem
        });
      }
    },

    /**
     * Align theme with OS preference
     * @param {ThemeState} state
     */
    syncWithSystem: (state) => {
      const systemPrefersDark = window.matchMedia?.('(prefers-color-scheme: dark)')?.matches;
      const newTheme = systemPrefersDark ? 'dark' : 'light';

      state.currentTheme = newTheme;
      state.prefersSystem = true;
      state.isSystemSynced = true;
      state.systemTheme = newTheme;
      state.error = null;

      // Sync with CSS
      syncCSSVariables(newTheme);

      // Persist if enabled
      if (state.persistPreference) {
        safeSetLocalStorage('themePreference', {
          theme: newTheme,
          prefersSystem: true
        });
      }
    },

    /**
     * Handle animation completion
     * @param {ThemeState} state
     */
    completeTransition: (state) => {
      state.isTransitioning = false;
    },

    /**
     * Update system theme detection
     * @param {ThemeState} state
     * @param {{payload: boolean}} action - Whether system prefers dark mode
     */
    updateSystemTheme: (state, action) => {
      state.systemTheme = action.payload ? 'dark' : 'light';

      // If synced with system, update current theme
      if (state.prefersSystem) {
        state.currentTheme = action.payload ? 'dark' : 'light';
        syncCSSVariables(state.currentTheme);

        // Persist if enabled
        if (state.persistPreference) {
          safeSetLocalStorage('themePreference', {
            theme: state.currentTheme,
            prefersSystem: true
          });
        }
      }
    },

    /**
     * Set error state
     * @param {ThemeState} state
     * @param {{payload: string}} action
     */
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

// Export actions
export const {
  toggleTheme,
  setTheme,
  setPreference,
  syncWithSystem,
  completeTransition,
  updateSystemTheme,
  setError,
} = themeSlice.actions;

// Export reducer
export default themeSlice.reducer;

/**
 * Selectors
 */

/**
 * Get current theme
 * @param {Object} state - Redux state
 * @returns {'light'|'dark'} Current theme
 */
export const selectCurrentTheme = (state) => state.theme.currentTheme;

/**
 * Check if dark mode is active
 * @param {Object} state - Redux state
 * @returns {boolean} True if dark mode is active
 */
export const selectIsDarkMode = (state) => state.theme.currentTheme === 'dark';

/**
 * Check if theme is transitioning
 * @param {Object} state - Redux state
 * @returns {boolean} True if transitioning
 */
export const selectTransitioning = (state) => state.theme.isTransitioning;

/**
 * Check if prefers system theme
 * @param {Object} state - Redux state
 * @returns {boolean} True if prefers system theme
 */
export const selectPrefersSystem = (state) => state.theme.prefersSystem;

/**
 * Get system theme preference
 * @param {Object} state - Redux state
 * @returns {'light'|'dark'} System theme preference
 */
export const selectSystemTheme = (state) => state.theme.systemTheme;

/**
 * Get any theme error
 * @param {Object} state - Redux state
 * @returns {string|null} Error message or null
 */
export const selectThemeError = (state) => state.theme.error;

/**
 * Initialize theme from persisted state
 * @returns {Function} Thunk to initialize theme
 */
export const initializeTheme = () => (dispatch) => {
  try {
    // Load from localStorage if available
    const savedPrefs = safeGetLocalStorage('themePreference', null);

    if (savedPrefs) {
      if (savedPrefs.prefersSystem) {
        dispatch(syncWithSystem());
      } else {
        dispatch(setTheme(savedPrefs.theme));
      }
    } else {
      // Default to system preference if no saved preference
      dispatch(syncWithSystem());
    }

    // Set up system preference listener
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      dispatch(updateSystemTheme(e.matches));
    });

  } catch (error) {
    console.error('Theme initialization failed:', error);
    dispatch(setError('Failed to initialize theme'));
  }
};