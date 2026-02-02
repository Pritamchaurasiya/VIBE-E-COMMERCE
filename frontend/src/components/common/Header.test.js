import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';
import { BrowserRouter } from 'react-router-dom';

// Mock dependencies
jest.mock('react-redux', () => ({
  useDispatch: () => jest.fn(),
  useSelector: () => false, // IsDarkMode false
}));

jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({
    logout: jest.fn(),
    isAuthenticated: true,
    user: { username: 'testuser' },
  }),
}));

jest.mock('../../utils/CartContext', () => ({
  useCart: () => ({
    cart: { item_count: 0 },
  }),
}));

// Mock useNavigate and useLocation
const mockedNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockedNavigate,
  useLocation: () => ({ pathname: '/' }),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders search input with visual shortcut hint', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );

    // Check for search input
    const searchInput = screen.getByPlaceholderText(/search products/i);
    expect(searchInput).toBeInTheDocument();

    // Check for the visual hint (/)
    // Since it's in a Box component, we might need to find it by text content
    const hint = screen.getByText('/');
    expect(hint).toBeInTheDocument();
  });

  test('focuses search input when "/" key is pressed', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );

    const searchInput = screen.getByPlaceholderText(/search products/i);

    // Press "/" key
    fireEvent.keyDown(window, { key: '/' });

    // Check if input is focused
    expect(searchInput).toHaveFocus();
  });

  test('does not focus search input when typing in another input', () => {
    render(
      <BrowserRouter>
        <div>
            <Header />
            <input data-testid="other-input" />
        </div>
      </BrowserRouter>
    );

    const searchInput = screen.getByPlaceholderText(/search products/i);
    const otherInput = screen.getByTestId('other-input');

    // Focus other input
    otherInput.focus();

    // Press "/" key
    fireEvent.keyDown(window, { key: '/' });

    // Check if search input is NOT focused (other input should still be focused)
    expect(searchInput).not.toHaveFocus();
    expect(otherInput).toHaveFocus();
  });
});
