// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";
import mockAxios from 'jest-mock-axios';

jest.mock('axios', () => mockAxios);

// Mock IntersectionObserver
class IntersectionObserver {
  observe() { return null; }
  unobserve() { return null; }
  disconnect() { return null; }
}

window.IntersectionObserver = IntersectionObserver;

afterEach(() => {
  mockAxios.reset();
});
