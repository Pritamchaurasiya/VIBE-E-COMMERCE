// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";

// Mock IntersectionObserver
class IntersectionObserver {
  observe() { return null; }
  unobserve() { return null; }
  disconnect() { return null; }
}
window.IntersectionObserver = IntersectionObserver;

// Mock Axios
jest.mock('axios', () => {
  const mockPromise = Promise.resolve({ data: {} });
  const mockFn = jest.fn(() => mockPromise);

  return {
    create: jest.fn(() => ({
      get: mockFn,
      post: mockFn,
      put: mockFn,
      delete: mockFn,
      patch: mockFn,
      interceptors: {
        request: { use: jest.fn(), eject: jest.fn() },
        response: { use: jest.fn(), eject: jest.fn() },
      },
      defaults: { headers: { common: {} } }
    })),
    get: mockFn,
    post: mockFn,
    put: mockFn,
    delete: mockFn,
    patch: mockFn,
    defaults: { headers: { common: {} } }
  };
});
