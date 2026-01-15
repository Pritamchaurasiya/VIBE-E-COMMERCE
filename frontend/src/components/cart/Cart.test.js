import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Cart from './Cart';
import { useCart } from '../../utils/CartContext';
import { useAuth } from '../../utils/AuthContext';

// Mock the contexts with factory to avoid importing the real files (and thus axios)
jest.mock('../../utils/CartContext', () => ({
  useCart: jest.fn(),
}));

jest.mock('../../utils/AuthContext', () => ({
  useAuth: jest.fn(),
}));

const mockCartItems = [
  {
    id: 1,
    name: 'Test Product 1',
    slug: 'test-product-1',
    price: 100,
    quantity: 2,
    total_price: 200,
    image: 'test-image-1.jpg',
    vendor_name: 'Vendor A',
    discount_percentage: 0
  },
  {
    id: 2,
    name: 'Test Product 2',
    slug: 'test-product-2',
    price: 50,
    quantity: 1,
    total_price: 50,
    image: 'test-image-2.jpg',
    vendor_name: 'Vendor B',
    discount_percentage: 10
  }
];

describe('Cart Component Accessibility', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({
      isAuthenticated: true
    });

    useCart.mockReturnValue({
      cart: {
        items: mockCartItems,
        item_count: 2,
        total_cost: 250
      },
      loading: false,
      updateCartItem: jest.fn(),
      removeFromCart: jest.fn(),
      clearCart: jest.fn()
    });
  });

  test('renders cart items with accessible quantity controls', () => {
    render(
      <BrowserRouter>
        <Cart />
      </BrowserRouter>
    );

    // These should exist after my changes
    const decreaseBtn1 = screen.getByLabelText('Decrease quantity of Test Product 1');
    const increaseBtn1 = screen.getByLabelText('Increase quantity of Test Product 1');

    expect(decreaseBtn1).toBeInTheDocument();
    expect(increaseBtn1).toBeInTheDocument();
  });

  test('renders item checkboxes with accessible labels', () => {
    render(
      <BrowserRouter>
        <Cart />
      </BrowserRouter>
    );

    // Select All Checkbox
    const selectAllCheckbox = screen.getByLabelText('Select all items');
    expect(selectAllCheckbox).toBeInTheDocument();

    // Individual Item Checkboxes
    const itemCheckbox1 = screen.getByLabelText('Select Test Product 1');
    expect(itemCheckbox1).toBeInTheDocument();
  });

  test('renders remove button with accessible label', () => {
     render(
      <BrowserRouter>
        <Cart />
      </BrowserRouter>
    );

    const removeBtn1 = screen.getByLabelText('Remove Test Product 1 from cart');
    expect(removeBtn1).toBeInTheDocument();
  });
});
