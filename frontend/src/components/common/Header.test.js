import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';
import { BrowserRouter } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';

// Mocks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

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

jest.mock('../../features/theme/themeSlice', () => ({
  selectIsDarkMode: () => false,
  toggleTheme: jest.fn(),
}));

jest.mock('react-redux', () => ({
  useDispatch: jest.fn(),
  useSelector: jest.fn(),
}));

// Mock useMediaQuery to prevent errors
jest.mock('@mui/material/useMediaQuery', () => () => false);

describe('Header Component', () => {
  beforeEach(() => {
    useDispatch.mockReturnValue(jest.fn());
    useSelector.mockReturnValue(false); // Default for isDarkMode
  });

  const renderHeader = () => {
    return render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
  };

  test('search input has placeholder with shortcut hint', () => {
    renderHeader();
    const searchInput = screen.getByPlaceholderText(/Search products... \(\/\)/i);
    expect(searchInput).toBeInTheDocument();
  });

  test('pressing / key focuses search input', () => {
    renderHeader();
    const searchInput = screen.getByRole('searchbox');

    // Ensure input is not focused initially
    expect(document.activeElement).not.toBe(searchInput);

    // Press '/' key
    fireEvent.keyDown(document, { key: '/' });

    // Ensure input is focused
    expect(document.activeElement).toBe(searchInput);
  });

  test('pressing / key does not focus search input if already typing in an input', () => {
    renderHeader();
    const searchInput = screen.getByRole('searchbox');

    // Create another input and focus it
    const otherInput = document.createElement('input');
    document.body.appendChild(otherInput);
    otherInput.focus();

    // Press '/' key
    fireEvent.keyDown(document, { key: '/' });

    // Focus should remain on the other input
    expect(document.activeElement).toBe(otherInput);
    expect(document.activeElement).not.toBe(searchInput);

    // Cleanup
    document.body.removeChild(otherInput);
  });
});
