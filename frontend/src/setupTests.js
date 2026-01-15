// src/setupTests.js
import "@testing-library/jest-dom";

// Mock IntersectionObserver
class IntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {
    return null;
  }
  unobserve() {
    return null;
  }
  disconnect() {
    return null;
  }
}

window.IntersectionObserver = IntersectionObserver;

// Mock matchMedia
window.matchMedia = window.matchMedia || function() {
  return {
    matches: false,
    addListener: function() {},
    removeListener: function() {}
  };
};

// Mock TextEncoder/TextDecoder
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock window.scrollTo
window.scrollTo = jest.fn();

// Mock console.error to avoid jsdom CSS errors
const originalConsoleError = console.error;
console.error = (...args) => {
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('Error: Could not parse CSS stylesheet') ||
     args[0].includes('Warning: React does not recognize the') ||
     args[0].includes('The above error occurred in the'))
  ) {
    return;
  }
  originalConsoleError(...args);
};

// Mock axios if needed globally, though transforming might handle it
jest.mock('axios', () => ({
  create: () => ({
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    put: jest.fn(() => Promise.resolve({ data: {} })),
    delete: jest.fn(() => Promise.resolve({ data: {} })),
  }),
}));
