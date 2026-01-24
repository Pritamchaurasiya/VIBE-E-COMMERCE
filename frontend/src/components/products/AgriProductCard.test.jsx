import React from 'react';
import { render, screen } from '@testing-library/react';
import AgriProductCard from './AgriProductCard';
import { BrowserRouter } from 'react-router-dom';
import { useCart } from '../../utils/CartContext';
import { useAuth } from '../../utils/AuthContext';

// Mocks with factory to prevent importing the actual files (which import axios)
jest.mock('../../utils/CartContext', () => ({
  useCart: jest.fn(),
}));

jest.mock('../../utils/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock react-router-dom hooks
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('AgriProductCard UX', () => {
  const mockProduct = {
    id: 1,
    name: 'Test Product',
    slug: 'test-product',
    price: 100,
    mrp: 120,
    image: '/test.jpg',
    packing_options: [
      { size: '1kg', price: 100 },
      { size: '5kg', price: 450 },
    ],
    in_wishlist: false,
    stock_quantity: 10,
    is_instant_pack: false,
    is_new: false,
    trending_score: 50,
  };

  const mockAddToCart = jest.fn();

  beforeEach(() => {
    useCart.mockReturnValue({ addToCart: mockAddToCart });
    useAuth.mockReturnValue({ isAuthenticated: true });
    jest.clearAllMocks();
  });

  test('renders price with correct currency symbol', () => {
    render(
      <BrowserRouter>
        <AgriProductCard product={mockProduct} />
      </BrowserRouter>
    );

    // We expect the correct Indian Rupee symbol
    // Initially this will fail because it's ? in the code
    const priceElements = screen.queryAllByText((content, node) => {
        return content.includes('₹') && (node.className.includes('agri-price-current') || node.className.includes('agri-price-mrp'));
    });
    // For reproduction, we assert that we DO NOT find it yet (or we find the broken one)
    // But to follow the plan "Create a reproduction test case... It will serve as verification for the fix",
    // it should be written to PASS when fixed and FAIL now.
    expect(priceElements.length).toBeGreaterThan(0);
  });

  test('packing options have accessibility attributes', () => {
    render(
      <BrowserRouter>
        <AgriProductCard product={mockProduct} />
      </BrowserRouter>
    );

    const packingButtons = screen.getAllByRole('button');
    const option1 = packingButtons.find(b => b.textContent === '1kg');
    const option2 = packingButtons.find(b => b.textContent === '5kg');

    // Check for aria-pressed
    expect(option1).toHaveAttribute('aria-pressed', 'true');
    expect(option2).toHaveAttribute('aria-pressed', 'false');

    // Check for group role and label
    const group = screen.getByRole('group', { name: /Select pack size for Test Product/i });
    expect(group).toBeInTheDocument();
  });

  test('add to cart button has descriptive aria-label', () => {
    render(
      <BrowserRouter>
        <AgriProductCard product={mockProduct} />
      </BrowserRouter>
    );

    // The button should include product name in its label
    const addToCartButton = screen.getByRole('button', { name: /Add Test Product to cart/i });
    expect(addToCartButton).toBeInTheDocument();
  });
});
