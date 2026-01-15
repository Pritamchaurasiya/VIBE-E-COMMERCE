import { render, screen } from "@testing-library/react";
import App from "./App";
import { Provider } from 'react-redux';
import { store } from './store';

test("renders app without crashing", () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );
  // Just checking if it renders without crashing for now, as specific text might change
});
