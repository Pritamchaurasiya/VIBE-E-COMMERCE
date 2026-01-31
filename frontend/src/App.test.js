import { render, screen } from "@testing-library/react";
import { Provider } from 'react-redux';
import { store } from './store';
import App from "./App";

test("renders VIBE E-Commerce title", async () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );
  const elements = await screen.findAllByText(/VIBE/i);
  expect(elements.length).toBeGreaterThan(0);
});
