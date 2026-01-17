import { render, screen, act } from "@testing-library/react";
import App from "./App";
import { Provider } from 'react-redux';
import { store } from './store';

test("renders app without crashing", async () => {
  // Use act to handle any useEffects or initial state updates
  await act(async () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
  });

  // Check for VIBE text which is present in the Header
  const vibeElements = screen.getAllByText(/VIBE/i);
  expect(vibeElements.length).toBeGreaterThan(0);
});
