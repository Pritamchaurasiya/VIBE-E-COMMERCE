/*
  Tests for serviceWorkerRegistration.js
  Framework: Jest (via CRA setupTests)
*/

// Ensure NODE_ENV can be toggled per test
const originalEnv = process.env.NODE_ENV;

// Helpers to mock navigator.serviceWorker
const mockServiceWorkerSupport = ({
  registerImpl = jest.fn(() => Promise.resolve({})),
  getRegistrationImpl = jest.fn(() => Promise.resolve({ unregister: jest.fn(() => Promise.resolve(true)) })),
} = {}) => {
  if (global.navigator === undefined) {
    global.navigator = {};
  }
  Object.defineProperty(global.navigator, 'serviceWorker', {
    value: {
      register: registerImpl,
      getRegistration: getRegistrationImpl,
      ready: Promise.resolve({}),
    },
    configurable: true,
    writable: true,
  });
  return { registerImpl, getRegistrationImpl };
};

const removeServiceWorker = () => {
  if (global.navigator && Object.getOwnPropertyDescriptor(global.navigator, 'serviceWorker')) {
    // eslint-disable-next-line no-undef
    delete global.navigator.serviceWorker;
  }
};

// Silence console noise but allow expectations
let consoleErrorSpy;
let consoleLogSpy;

beforeEach(() => {
  consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
});

afterEach(() => {
  removeServiceWorker();
  consoleErrorSpy.mockRestore();
  consoleLogSpy.mockRestore();
  process.env.NODE_ENV = originalEnv;
});

// Some CRA templates register on window load; mock addEventListener to immediately invoke listener
const triggerWindowLoad = () => {
  const listeners = [];
  // Use global.window if window is not defined
  const target = typeof window !== 'undefined' ? window : global.window;

  const addEventListenerSpy = jest
    .spyOn(target, 'addEventListener')
    .mockImplementation((event, cb) => {
      if (event === 'load') listeners.push(cb);
    });
  // Return a function to trigger all load listeners and restore spy
  return {
    fire: () => listeners.forEach((cb) => cb()),
    restore: () => addEventListenerSpy.mockRestore(),
  };
};

// Dynamically import the module so that env/mocks take effect per test
const importSWR = async () => {
  jest.resetModules();
  // Absolute path relative to this file
  const mod = await import('./serviceWorkerRegistration');
  return mod;
};


describe('serviceWorkerRegistration', () => {
  test('Should register service worker in production environment when supported by the browser', async () => {
    process.env.NODE_ENV = 'production';

    const { registerImpl } = mockServiceWorkerSupport();
    const loader = triggerWindowLoad();

    // Import after setting env and mocks
    const swr = await importSWR();

    // Some implementations export register() that binds to load internally; call register to set up
    if (swr.register) swr.register();

    // Simulate window load
    loader.fire();
    loader.restore();

    // Ensure register called with expected script path
    expect(registerImpl).toHaveBeenCalled();
  });

  test('Should not register service worker in development environment', async () => {
    process.env.NODE_ENV = 'development';

    const { registerImpl } = mockServiceWorkerSupport();
    const loader = triggerWindowLoad();

    const swr = await importSWR();
    if (swr.register) swr.register();

    loader.fire();
    loader.restore();

    expect(registerImpl).not.toHaveBeenCalled();
  });

  test('Should unregister service worker when unregister is called and service workers are supported', async () => {
    process.env.NODE_ENV = 'production';

    const unregisterMock = jest.fn(() => Promise.resolve(true));
    const getRegistrationImpl = jest.fn(() => Promise.resolve({ unregister: unregisterMock }));
    mockServiceWorkerSupport({ getRegistrationImpl });

    const swr = await importSWR();
    expect(typeof swr.unregister).toBe('function');

    await swr.unregister();

    expect(getRegistrationImpl).toHaveBeenCalled();
    expect(unregisterMock).toHaveBeenCalled();
  });

  test('Should handle registration failure by logging an error without throwing', async () => {
    process.env.NODE_ENV = 'production';

    const error = new Error('network fail');
    const registerImpl = jest.fn(() => Promise.reject(error));
    mockServiceWorkerSupport({ registerImpl });

    const loader = triggerWindowLoad();
    const swr = await importSWR();
    if (swr.register) swr.register();

    await Promise.resolve().then(() => {}); // allow microtasks to flush

    loader.fire();
    loader.restore();

    // Allow any catch handlers to execute
    await new Promise((r) => setTimeout(r, 0));

    expect(consoleErrorSpy).toHaveBeenCalled();
  });

  test('Should skip registration gracefully if service workers are not supported', async () => {
    process.env.NODE_ENV = 'production';

    // Ensure no serviceWorker on navigator
    removeServiceWorker();

    const loader = triggerWindowLoad();

    const swr = await importSWR();
    if (swr.register) swr.register();

    loader.fire();
    loader.restore();

    // No error should be logged, and nothing to assert on register calls
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });
});
