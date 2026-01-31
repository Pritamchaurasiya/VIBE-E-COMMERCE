import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
  Link: ({ children, ...props }) => <a {...props}>{children}</a>,
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

jest.mock('react-redux', () => ({
  useDispatch: () => jest.fn(),
  useSelector: () => false, // selectIsDarkMode returns boolean
}));

jest.mock('framer-motion', () => ({
  ...jest.requireActual('framer-motion'),
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

describe('Header Component', () => {
  test('focuses search input when "/" is pressed', () => {
    render(<Header />);

    const searchInput = screen.getByRole('searchbox', { name: /search products/i });

    // Initial check: not focused
    expect(searchInput).not.toHaveFocus();

    // Press "/"
    fireEvent.keyDown(window, { key: '/' });

    // Check if focused
    expect(searchInput).toHaveFocus();
  });

  test('focuses search input when "Ctrl+K" is pressed', () => {
    render(<Header />);

    const searchInput = screen.getByRole('searchbox', { name: /search products/i });

    expect(searchInput).not.toHaveFocus();

    // Press "Ctrl+K"
    fireEvent.keyDown(window, { key: 'k', ctrlKey: true });

    expect(searchInput).toHaveFocus();
  });

  test('does not focus search input when typing in another input', () => {
    render(
      <div>
        <Header />
        <input data-testid="other-input" />
      </div>
    );

    const otherInput = screen.getByTestId('other-input');
    const searchInput = screen.getByRole('searchbox', { name: /search products/i });

    // Focus other input
    otherInput.focus();

    // Press "/"
    fireEvent.keyDown(window, { key: '/' });

    // Search input should NOT be focused, otherInput should remain focused
    expect(searchInput).not.toHaveFocus();
    expect(otherInput).toHaveFocus();
  });
});
