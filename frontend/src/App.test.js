import { render, screen, act } from "@testing-library/react";
import App from "./App";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import themeReducer from "./features/theme/themeSlice";

// Create a mock store for testing
const store = configureStore({
  reducer: {
    theme: themeReducer,
  },
});

test("renders app without crashing", async () => {
  await act(async () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
  });
  // Simple test to ensure it mounts
  // expect(screen.getByText(/VIBE/i)).toBeInTheDocument();
});
