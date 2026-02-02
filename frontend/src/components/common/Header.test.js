import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';
import { BrowserRouter } from 'react-router-dom';

// Mocks
jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({
    logout: jest.fn(),
    isAuthenticated: false,
    user: null,
  }),
}));

jest.mock('../../utils/CartContext', () => ({
  useCart: () => ({
    cart: { item_count: 0 },
  }),
}));

jest.mock('react-redux', () => ({
  useDispatch: () => jest.fn(),
  useSelector: () => false, // isDarkMode
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

// Mock useMediaQuery to avoid issues with responsive checks
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  useMediaQuery: () => false,
}));

test('focuses search input when / is pressed', () => {
  render(
    <BrowserRouter>
      <Header />
    </BrowserRouter>
  );

  const searchInput = screen.getByRole('searchbox', { name: /search products/i });
  expect(searchInput).not.toHaveFocus();

  fireEvent.keyDown(window, { key: '/' });

  expect(searchInput).toHaveFocus();
});

test('does not focus search input when / is pressed inside an input', () => {
  render(
    <BrowserRouter>
      <Header />
      <input data-testid="other-input" />
    </BrowserRouter>
  );

  const searchInput = screen.getByRole('searchbox', { name: /search products/i });
  const otherInput = screen.getByTestId('other-input');

  otherInput.focus();
  fireEvent.keyDown(otherInput, { key: '/' });

  expect(searchInput).not.toHaveFocus();
  expect(otherInput).toHaveFocus();
});

test('search input has helper text in placeholder', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );

    const searchInput = screen.getByPlaceholderText(/search products... \(\/\)/i);
    expect(searchInput).toBeInTheDocument();
  });
