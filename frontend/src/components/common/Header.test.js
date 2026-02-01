import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from './Header';
import { MemoryRouter } from 'react-router-dom';

// Mock dependencies
jest.mock('react-redux', () => ({
  useDispatch: () => jest.fn(),
  useSelector: () => false, // Default to light mode
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

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

// Mock MUI useMediaQuery to force desktop view
jest.mock('@mui/material', () => ({
    ...jest.requireActual('@mui/material'),
    useMediaQuery: () => false,
}));


describe('Header Component', () => {
  test('focuses search input when / key is pressed', () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );

    const searchInput = screen.getByRole('searchbox', { name: /search products/i });
    expect(searchInput).toBeInTheDocument();
    expect(document.activeElement).not.toBe(searchInput);

    // Simulate pressing "/"
    fireEvent.keyDown(window, { key: '/' });

    expect(document.activeElement).toBe(searchInput);
  });

  test('does not focus search input when typing / inside another input', () => {
     render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );

    const searchInput = screen.getByRole('searchbox', { name: /search products/i });

    // create another input
    const otherInput = document.createElement('input');
    document.body.appendChild(otherInput);
    otherInput.focus();

    fireEvent.keyDown(otherInput, { key: '/' });

    expect(document.activeElement).toBe(otherInput);
    expect(document.activeElement).not.toBe(searchInput);

    document.body.removeChild(otherInput);
  });
});
