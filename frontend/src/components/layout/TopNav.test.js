import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TopNav from './TopNav';
import { BrowserRouter } from 'react-router-dom';

// Mocks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

jest.mock('../../utils/CartContext', () => ({
  useCart: () => ({ cartCount: 0 }),
}));

jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: false }),
}));

jest.mock('../../services/api', () => ({
  productsAPI: {
    search: jest.fn().mockResolvedValue({ data: { results: [] } }),
  },
}));

describe('TopNav Component', () => {
  test('focuses search input when / is pressed', () => {
    render(
      <BrowserRouter>
        <TopNav />
      </BrowserRouter>
    );

    const searchInput = screen.getByPlaceholderText(/Search seeds, fertilizers/i);

    // Initial check: not focused
    expect(searchInput).not.toHaveFocus();

    // Press /
    fireEvent.keyDown(window, { key: '/' });

    // Should be focused
    expect(searchInput).toHaveFocus();
  });

  test('focuses search input when Ctrl+K is pressed', () => {
    render(
      <BrowserRouter>
        <TopNav />
      </BrowserRouter>
    );

    const searchInput = screen.getByPlaceholderText(/Search seeds, fertilizers/i);

    // Press Ctrl+K
    fireEvent.keyDown(window, { key: 'k', ctrlKey: true });

    // Should be focused
    expect(searchInput).toHaveFocus();
  });

  test('does not focus search input when typing / in another input', () => {
    render(
      <BrowserRouter>
        <div>
           <input data-testid="other-input" />
           <TopNav />
        </div>
      </BrowserRouter>
    );

    const otherInput = screen.getByTestId('other-input');
    const searchInput = screen.getByPlaceholderText(/Search seeds, fertilizers/i);

    otherInput.focus();

    // Press / while in other input
    fireEvent.keyDown(otherInput, { key: '/' });

    // Should still be in other input
    expect(otherInput).toHaveFocus();
    expect(searchInput).not.toHaveFocus();
  });
});
