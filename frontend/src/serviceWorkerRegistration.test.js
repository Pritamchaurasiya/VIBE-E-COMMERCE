/*
  Tests for serviceWorkerRegistration.js
  Framework: Jest (via CRA setupTests)
*/

// Ensure NODE_ENV can be toggled per test
const originalEnv = process.env.NODE_ENV;

// Helpers to mock navigator.serviceWorker
const mockServiceWorkerSupport = ({
  registerImpl = jest.fn(() => Promise.resolve({
    installing: null,
    onupdatefound: null
  })),
  getRegistrationImpl = jest.fn(() => Promise.resolve({ unregister: jest.fn(() => Promise.resolve(true)) })),
} = {}) => {
  // We need to define it on global.navigator
  // But JSDOM might have it read-only or not configurable.
  // We'll try to redefine it.

  if (!global.navigator) {
    global.navigator = {};
  }

  try {
    Object.defineProperty(global.navigator, 'serviceWorker', {
      value: {
        register: registerImpl,
        getRegistration: getRegistrationImpl,
        ready: Promise.resolve({
            unregister: jest.fn(() => Promise.resolve(true))
        }),
      },
      configurable: true,
      writable: true
    });
  } catch (e) {
    // Fallback if property is not configurable
    global.navigator.serviceWorker = {
      register: registerImpl,
      getRegistration: getRegistrationImpl,
      ready: Promise.resolve({
          unregister: jest.fn(() => Promise.resolve(true))
      }),
    };
  }
  return { registerImpl, getRegistrationImpl };
};

const removeServiceWorker = () => {
    // @ts-ignore
    delete global.navigator.serviceWorker;
};

// Silence console noise but allow expectations
let consoleErrorSpy;
let consoleLogSpy;

beforeEach(() => {
  consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

  // Mock window.location
  delete window.location;
  window.location = {
    ...window.location,
    hostname: 'example.com',
    href: 'http://example.com/',
    origin: 'http://example.com'
  };
});

afterEach(() => {
  // removeServiceWorker();
  jest.restoreAllMocks();
  process.env.NODE_ENV = originalEnv;
});

// Some CRA templates register on window load; mock addEventListener to immediately invoke listener
const triggerWindowLoad = () => {
  const listeners = [];
  const addEventListenerSpy = jest
    .spyOn(window, 'addEventListener')
    .mockImplementation((event, cb) => {
      if (event === 'load') listeners.push(cb);
    });
  // Return a function to trigger all load listeners and restore spy
  return {
    fire: () => listeners.forEach((cb) => cb()),
    restore: () => addEventListenerSpy.mockRestore(),
  };
};

describe('serviceWorkerRegistration', () => {
  test('Should register service worker in production environment when supported by the browser', async () => {
    process.env.NODE_ENV = 'production';
    process.env.PUBLIC_URL = '';

    const { registerImpl } = mockServiceWorkerSupport();
    const loader = triggerWindowLoad();

    // We need to re-require because the module runs code on import (checking env)
    jest.isolateModules(() => {
        const swr = require('./serviceWorkerRegistration');
        swr.register();
    });

    // Simulate window load
    loader.fire();

    // Ensure register called with expected script path
    expect(registerImpl).toHaveBeenCalled();
  });

  test('Should not register service worker in development environment', async () => {
    process.env.NODE_ENV = 'development';

    const { registerImpl } = mockServiceWorkerSupport();
    const loader = triggerWindowLoad();

    jest.isolateModules(() => {
        const swr = require('./serviceWorkerRegistration');
        swr.register();
    });

    loader.fire();

    expect(registerImpl).not.toHaveBeenCalled();
  });

  test('Should unregister service worker when unregister is called and service workers are supported', async () => {
    process.env.NODE_ENV = 'production';

    const unregisterMock = jest.fn(() => Promise.resolve(true));
    // We need to mock .ready to return the registration that has unregister
    Object.defineProperty(global.navigator, 'serviceWorker', {
        value: {
            ready: Promise.resolve({
                unregister: unregisterMock
            })
        },
        configurable: true,
        writable: true
    });

    jest.isolateModules(async () => {
        const swr = require('./serviceWorkerRegistration');
        await swr.unregister();
    });

    // Wait for promise to resolve
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(unregisterMock).toHaveBeenCalled();
  });

  test('Should handle registration failure by logging an error without throwing', async () => {
    process.env.NODE_ENV = 'production';
    process.env.PUBLIC_URL = '';

    const error = new Error('network fail');
    const registerImpl = jest.fn(() => Promise.reject(error));
    mockServiceWorkerSupport({ registerImpl });

    const loader = triggerWindowLoad();

    jest.isolateModules(() => {
        const swr = require('./serviceWorkerRegistration');
        swr.register();
    });

    loader.fire();

    // Allow any catch handlers to execute
    await new Promise((r) => setTimeout(r, 0));

    expect(consoleErrorSpy).toHaveBeenCalled();
  });
});
