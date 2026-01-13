import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AgriProductCard from './AgriProductCard';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../utils/AuthContext';
import { CartProvider } from '../../utils/CartContext';

// Mock store
const mockStore = configureStore({
  reducer: {
    cart: (state = { items: [] }, action) => state,
    wishlist: (state = { items: [] }, action) => state,
  },
});

const mockProduct = {
  id: 1,
  name: 'Test Product',
  price: 100,
  image: 'test.jpg',
  category: 'Seeds',
  vendor: 'Test Vendor',
  is_in_stock: true,
  stock_quantity: 50,
  rating: 4.5,
  review_count: 10
};

const renderWithProviders = (component) => {
  return render(
    <Provider store={mockStore}>
      <BrowserRouter>
        <AuthProvider>
          <CartProvider>
            {component}
          </CartProvider>
        </AuthProvider>
      </BrowserRouter>
    </Provider>
  );
};

describe('AgriProductCard', () => {
  test('renders product information correctly', () => {
    renderWithProviders(<AgriProductCard product={mockProduct} />);

    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText(/₹100/)).toBeInTheDocument();
  });

  test('renders add to cart button', () => {
    renderWithProviders(<AgriProductCard product={mockProduct} />);

    expect(screen.getByLabelText(/Add Test Product to cart/i)).toBeInTheDocument();
  });
});
