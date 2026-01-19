import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AgriProductCard from './AgriProductCard';
import { BrowserRouter } from 'react-router-dom';

// Mock contexts
jest.mock('../../utils/CartContext', () => ({
  useCart: () => ({ addToCart: jest.fn() }),
}));

jest.mock('../../utils/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
}));

const mockProduct = {
  id: 1,
  name: 'Test Product',
  slug: 'test-product',
  price: 100,
  packing_options: [
    { size: '1kg', price: 100 },
    { size: '5kg', price: 450 },
  ],
};

test('renders packing options with accessibility attributes', () => {
  render(
    <BrowserRouter>
      <AgriProductCard product={mockProduct} />
    </BrowserRouter>
  );

  const pack1Button = screen.getByRole('button', { name: /Select 1kg pack/i });
  const pack5Button = screen.getByRole('button', { name: /Select 5kg pack/i });

  expect(pack1Button).toBeInTheDocument();
  expect(pack5Button).toBeInTheDocument();

  // Initial state: first option selected
  expect(pack1Button).toHaveAttribute('aria-pressed', 'true');
  expect(pack5Button).toHaveAttribute('aria-pressed', 'false');

  // Click second option
  fireEvent.click(pack5Button);

  expect(pack1Button).toHaveAttribute('aria-pressed', 'false');
  expect(pack5Button).toHaveAttribute('aria-pressed', 'true');
});
