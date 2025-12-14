import CryptoJS from 'crypto-js';
import { v4 as uuidv4 } from 'uuid';

// Security Constants
export const SECURITY_CONSTANTS = {
  TOKEN_STORAGE_KEY: 'auth_token',
  REFRESH_TOKEN_STORAGE_KEY: 'refresh_token',
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  MAX_FAILED_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15 * 60 * 1000, // 15 minutes
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_COMPLEXITY_REGEX: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  JWT_SECRET: process.env.REACT_APP_JWT_SECRET,
  ENCRYPTION_KEY: process.env.REACT_APP_ENCRYPTION_KEY
};

// Token Management
export const setAuthToken = (token) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(SECURITY_CONSTANTS.TOKEN_STORAGE_KEY, token);
  }
};

export const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(SECURITY_CONSTANTS.TOKEN_STORAGE_KEY);
  }
  return null;
};

export const removeAuthToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(SECURITY_CONSTANTS.TOKEN_STORAGE_KEY);
    localStorage.removeItem(SECURITY_CONSTANTS.REFRESH_TOKEN_STORAGE_KEY);
  }
};

export const setRefreshToken = (token) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(SECURITY_CONSTANTS.REFRESH_TOKEN_STORAGE_KEY, token);
  }
};

export const getRefreshToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(SECURITY_CONSTANTS.REFRESH_TOKEN_STORAGE_KEY);
  }
  return null;
};

// Data Encryption
export const encryptData = (data, key = SECURITY_CONSTANTS.ENCRYPTION_KEY) => {
  try {
    if (!data) return null;
    const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key);
    return encrypted.toString();
  } catch (error) {
    console.error('Encryption failed:', error);
    return null;
  }
};

export const decryptData = (encryptedData, key = SECURITY_CONSTANTS.ENCRYPTION_KEY) => {
  try {
    if (!encryptedData) return null;
    const decrypted = CryptoJS.AES.decrypt(encryptedData, key);
    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
  } catch (error) {
    console.error('Decryption failed:', error);
    return null;
  }
};

// Password Validation
export const validatePassword = (password) => {
  if (!password || password.length < SECURITY_CONSTANTS.PASSWORD_MIN_LENGTH) {
    return { valid: false, message: `Password must be at least ${SECURITY_CONSTANTS.PASSWORD_MIN_LENGTH} characters long` };
  }

  if (!SECURITY_CONSTANTS.PASSWORD_COMPLEXITY_REGEX.test(password)) {
    return {
      valid: false,
      message: 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
    };
  }

  return { valid: true, message: 'Password is valid' };
};

// Session Management
export const checkSessionTimeout = (lastActivity) => {
  const currentTime = Date.now();
  return currentTime - lastActivity > SECURITY_CONSTANTS.SESSION_TIMEOUT;
};

export const generateSessionId = () => {
  return uuidv4();
};

// CSRF Protection
export const getCsrfToken = () => {
  if (typeof window !== 'undefined') {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : null;
  }
  return null;
};

// Secure Local Storage
export const secureLocalStorage = {
  setItem: (key, value) => {
    try {
      const encryptedValue = encryptData(value);
      if (typeof window !== 'undefined' && encryptedValue) {
        localStorage.setItem(key, encryptedValue);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Secure storage failed:', error);
      return false;
    }
  },

  getItem: (key) => {
    try {
      if (typeof window !== 'undefined') {
        const encryptedValue = localStorage.getItem(key);
        return decryptData(encryptedValue);
      }
      return null;
    } catch (error) {
      console.error('Secure storage retrieval failed:', error);
      return null;
    }
  },

  removeItem: (key) => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
  }
};

// Input Sanitization
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;

  // Basic XSS protection
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

// Rate Limiting (client-side simulation)
export const rateLimiter = (() => {
  const attempts = new Map();

  return {
    check: (key, maxAttempts = SECURITY_CONSTANTS.MAX_FAILED_ATTEMPTS, duration = SECURITY_CONSTANTS.LOCKOUT_DURATION) => {
      const now = Date.now();
      const attemptData = attempts.get(key) || { count: 0, firstAttempt: now };

      // Check if lockout period has passed
      if (now - attemptData.firstAttempt > duration) {
        attempts.delete(key);
        return { allowed: true, retryAfter: 0 };
      }

      // Check if attempts exceeded
      if (attemptData.count >= maxAttempts) {
        const retryAfter = duration - (now - attemptData.firstAttempt);
        return { allowed: false, retryAfter };
      }

      // Increment attempt count
      attemptData.count++;
      attempts.set(key, attemptData);
      return { allowed: true, retryAfter: 0 };
    },

    reset: (key) => {
      attempts.delete(key);
    }
  };
})();

// Security Headers Check (client-side)
export const checkSecurityHeaders = () => {
  if (typeof document !== 'undefined') {
    const headers = {
      'Content-Security-Policy': document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content,
      'X-Content-Type-Options': document.querySelector('meta[http-equiv="X-Content-Type-Options"]')?.content,
      'X-Frame-Options': document.querySelector('meta[http-equiv="X-Frame-Options"]')?.content,
      'Strict-Transport-Security': document.querySelector('meta[http-equiv="Strict-Transport-Security"]')?.content
    };

    return headers;
  }

  return {};
};

// JWT Token Validation (basic client-side check)
export const validateJwtToken = (token) => {
  if (!token) return false;

  try {
    // This is a basic check - real validation should happen server-side
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    // Check token structure
    const header = JSON.parse(atob(parts[0]));
    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    if (payload.exp && Date.now() >= payload.exp * 1000) {
      return false;
    }

    return true;
  } catch (error) {
    console.error('Token validation error:', error);
    return false;
  }
};

// Secure API Request Wrapper
export const secureApiRequest = async (url, options = {}, requireAuth = true) => {
  try {
    // Add auth token if required
    if (requireAuth) {
      const token = getAuthToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
    }

    // Add CSRF token if available
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      options.headers = {
        ...options.headers,
        'X-CSRF-Token': csrfToken
      };
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      if (response.status === 401) {
        // Handle unauthorized - token might be expired
        removeAuthToken();
        throw new Error('Session expired. Please log in again.');
      }

      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Secure API request failed:', error);
    throw error;
  }
};

// Export all security utilities
export default {
  ...SECURITY_CONSTANTS,
  setAuthToken,
  getAuthToken,
  removeAuthToken,
  setRefreshToken,
  getRefreshToken,
  encryptData,
  decryptData,
  validatePassword,
  checkSessionTimeout,
  generateSessionId,
  getCsrfToken,
  secureLocalStorage,
  sanitizeInput,
  rateLimiter,
  checkSecurityHeaders,
  validateJwtToken,
  secureApiRequest
};