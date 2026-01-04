// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";

// Mock axios to avoid ESM issues in test environment
import mockAxios from 'jest-mock-axios';
jest.mock('axios', () => mockAxios);

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor(callback, options) {}
  observe(element) {}
  unobserve(element) {}
  disconnect() {}
};
