import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import themeReducer from '../../features/theme/themeSlice';

// Mock contexts
jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: false,
    user: null,
    logout: jest.fn(),
  }),
}));

jest.mock('../../utils/CartContext', () => ({
  useCart: () => ({
    cart: { item_count: 0 },
  }),
}));

// Mock MUI useMediaQuery
jest.mock('@mui/material', () => {
  const actual = jest.requireActual('@mui/material');
  return {
    ...actual,
    useMediaQuery: () => false,
  };
});

// Setup Redux store
const store = configureStore({
  reducer: {
    theme: themeReducer,
  },
});

const renderHeader = () => {
  return render(
    <Provider store={store}>
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    </Provider>
  );
};

test('focuses search input when / key is pressed', () => {
  renderHeader();

  const searchInput = screen.getByRole('searchbox', { name: /search products/i });
  expect(searchInput).not.toHaveFocus();

  fireEvent.keyDown(window, { key: '/' });

  expect(searchInput).toHaveFocus();
});

test('does not focus search input when / key is pressed inside another input', () => {
  renderHeader();

  const searchInput = screen.getByRole('searchbox', { name: /search products/i });

  // Create another input and focus it
  const otherInput = document.createElement('input');
  document.body.appendChild(otherInput);
  otherInput.focus();

  fireEvent.keyDown(window, { key: '/' });

  expect(searchInput).not.toHaveFocus();
  expect(otherInput).toHaveFocus();

  document.body.removeChild(otherInput);
});
