import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AgriProductCard from './AgriProductCard';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  Link: ({ children, to, ...props }) => <a href={to} {...props}>{children}</a>,
  useNavigate: () => jest.fn(),
}));

jest.mock('../../utils/CartContext', () => ({
  useCart: () => ({
    addToCart: jest.fn(),
  }),
}));

jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
  }),
}));

const mockProduct = {
  id: 1,
  name: "Test Product",
  slug: "test-product",
  price: 100,
  image: "test.jpg",
  brand: "TestBrand",
  mrp: 120,
  unit: "1 kg",
  packing_options: [
    { size: "1 kg", price: 100 },
    { size: "5 kg", price: 450 },
  ],
  is_instant_pack: false,
  is_new: false,
  trending_score: 50,
  in_wishlist: false,
};

describe('AgriProductCard UX/A11y', () => {
  test('renders packing options with correct accessibility attributes', () => {
    render(<AgriProductCard product={mockProduct} />);

    const pack1 = screen.getByText('1 kg');
    const pack2 = screen.getByText('5 kg');

    // These should ideally fail before my fix
    // Checking for ARIA pressed state
    // Note: buttons usually don't have aria-pressed by default unless we add it

    // We want to check if the selected option is indicated to screen readers
    // Initially, the first one is selected.
    expect(pack1).toHaveClass('active');
    expect(pack2).not.toHaveClass('active');

    // In a good accessible implementation:
    // 1. The container should have role="group" and aria-label
    // 2. The buttons should have aria-pressed or aria-selected

    // Let's check if the parent of the buttons has role="group"
    // pack1.parentElement check

    // I'll leave these commented out to demonstrate what I'm looking for,
    // but the test should assert the *current* state first or fail on the *desired* state.

    // Checking for ARIA pressed state
    expect(pack1).toHaveAttribute('aria-pressed', 'true');
    expect(pack2).toHaveAttribute('aria-pressed', 'false');
    expect(pack1.parentElement).toHaveAttribute('role', 'group');
    expect(pack1.parentElement).toHaveAttribute('aria-label', 'Packing options for Test Product');
  });

  test('displays currency symbol correctly', () => {
    render(<AgriProductCard product={mockProduct} />);

    // Should render Indian Rupee symbol
    const priceElement = screen.getByText((content) => content.includes('100'));
    expect(priceElement).toHaveTextContent('₹100');
  });
});
