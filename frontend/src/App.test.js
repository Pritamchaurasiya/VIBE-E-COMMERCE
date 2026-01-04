import { render, screen } from "@testing-library/react";
import App from "./App";
import { Provider } from 'react-redux';
import { store } from './store';
import { act } from 'react-dom/test-utils';
import mockAxios from 'jest-mock-axios';

afterEach(() => {
  mockAxios.reset();
});

test("renders app without crashing", async () => {
  // Mock initial API calls that happen on mount
  mockAxios.get.mockResolvedValueOnce({ data: { user: null } }); // Auth check
  mockAxios.get.mockResolvedValueOnce({ data: { items: [], total_cost: 0, item_count: 0 } }); // Cart load

  await act(async () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
  });

  // Use getAllByText since "VIBE" appears multiple times (Logo text, Footer text, etc.)
  const logoElements = screen.getAllByText(/VIBE/i);
  expect(logoElements.length).toBeGreaterThan(0);
});
