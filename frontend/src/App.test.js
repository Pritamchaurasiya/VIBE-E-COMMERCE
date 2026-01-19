import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { store } from "./store";
import App from "./App";
import { act } from "react";

test("renders learn react link", async () => {
  await act(async () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
  });

  const linkElements = screen.getAllByText(/VIBE/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
