import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import Header from './Header';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';

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

jest.mock('../../features/theme/themeSlice', () => ({
  selectIsDarkMode: jest.fn(() => false),
  toggleTheme: jest.fn(),
}));

// Mock useMediaQuery from MUI
jest.mock('@mui/material/useMediaQuery', () => jest.fn(() => false));

// Mock Redux store
const mockStore = configureStore({
  reducer: {
    theme: (state = { isDarkMode: false }) => state,
  },
});

describe('Header Component UX', () => {
  test('focuses search input when "/" key is pressed', () => {
    render(
      <Provider store={mockStore}>
        <MemoryRouter>
          <Header />
        </MemoryRouter>
      </Provider>
    );

    const searchInput = screen.getByRole('searchbox', { name: /search products/i });
    expect(document.activeElement).not.toBe(searchInput);

    fireEvent.keyDown(window, { key: '/' });

    expect(document.activeElement).toBe(searchInput);
  });

  test('does not focus search input when another input is active', () => {
     render(
      <Provider store={mockStore}>
        <MemoryRouter>
          <Header />
          <input type="text" aria-label="Other Input" />
        </MemoryRouter>
      </Provider>
    );

    const searchInput = screen.getByRole('searchbox', { name: /search products/i });
    const otherInput = screen.getByLabelText('Other Input');

    otherInput.focus();
    fireEvent.keyDown(window, { key: '/' });

    expect(document.activeElement).toBe(otherInput);
  });
});
