import { render, screen } from "@testing-library/react";
import App from "./App";
import { Provider } from 'react-redux';
import { store } from './store';

test("renders VIBE E-Commerce text", () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );

  // Use getAllByText because VIBE appears multiple times (Logo, Menu items, Footer, etc)
  // We just want to ensure at least one instance exists to verify the app renders.
  const linkElements = screen.getAllByText(/VIBE/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
