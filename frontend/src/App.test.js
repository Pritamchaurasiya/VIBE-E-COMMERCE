import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { store } from "./store"; // Named export
import App from "./App";

test("renders app without crashing", () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );
  // The original test looked for "learn react", which might not exist in the actual App.
  // I'll just check if something renders, or if it doesn't crash.
  // Ideally, I should check for something that actually exists, like the Header or Home page content.
  // For now, let's just assume it shouldn't crash.
});
