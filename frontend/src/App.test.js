import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { store } from "./store";
import App from "./App";

test("renders VIBE brand text", () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );
  const linkElement = screen.getAllByText(/VIBE/i)[0];
  expect(linkElement).toBeInTheDocument();
});
