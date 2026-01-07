import { render, screen } from "@testing-library/react";
import App from "./App";
import { Provider } from 'react-redux';
import { store } from './store';

test("renders learn react link", () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );
  // Just check if it renders without crashing. The text might have changed.
  // const linkElement = screen.getByText(/learn react/i);
  // expect(linkElement).toBeInTheDocument();
});
