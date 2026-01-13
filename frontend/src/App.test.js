import React from "react";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { store } from "./store";
import App from "./App";
import { act } from "react";

// Mock intersection observer since it's not available in jsdom
class MockIntersectionObserver {
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
}

window.IntersectionObserver = MockIntersectionObserver;

test("renders app without crashing", async () => {
  await act(async () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
  });
  // Just checking if it renders, specific text might change
  const linkElement = screen.getByRole("banner"); // Header usually has banner role
  expect(linkElement).toBeInTheDocument();
});
