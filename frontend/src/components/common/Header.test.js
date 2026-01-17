import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';
import { BrowserRouter } from 'react-router-dom';

// Mock dependencies
jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { first_name: 'Test', username: 'User' },
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
  useSelector: () => false, // isDarkMode = false
}));

jest.mock('../../features/theme/themeSlice', () => ({
  toggleTheme: jest.fn(),
  selectIsDarkMode: jest.fn(),
}));

// Mock framer-motion to avoid issues
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

describe('Header Component', () => {
  test('renders search bar and handles interactions', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );

    // Check if search input exists
    const searchInput = screen.getByPlaceholderText(/search products.../i);
    expect(searchInput).toBeInTheDocument();

    // Check if search button exists (aria-label="search products")
    // Note: there are two search buttons, mobile and desktop.
    // The desktop one we modified has aria-label="search products"
    // The mobile one has aria-label="submit search"
    const searchButtons = screen.getAllByLabelText(/search products/i);
    expect(searchButtons.length).toBeGreaterThan(0);

    // Type in search
    fireEvent.change(searchInput, { target: { value: 'Seeds' } });
    expect(searchInput.value).toBe('Seeds');

    // Check if clear button appears
    const clearButton = screen.getByLabelText(/clear search/i);
    expect(clearButton).toBeInTheDocument();

    // Click clear button
    fireEvent.click(clearButton);
    expect(searchInput.value).toBe('');

    // Clear button should disappear
    expect(screen.queryByLabelText(/clear search/i)).not.toBeInTheDocument();
  });
});
