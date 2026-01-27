import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchAutocomplete from './SearchAutocomplete';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

// Mock API
jest.mock('../../services/api', () => ({
  productsAPI: {
    getProducts: jest.fn(),
  },
}));

describe('SearchAutocomplete Component', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('Clear History button should be accessible', () => {
    // Setup local storage with some history
    localStorage.setItem('vibe_search_history', JSON.stringify(['apple']));

    render(<SearchAutocomplete />);

    // Click on input to show suggestions
    const input = screen.getByPlaceholderText(/search products/i);
    fireEvent.focus(input);

    // The "Clear" text should be visible
    const clearText = screen.getByText('Clear');
    expect(clearText).toBeInTheDocument();

    // It should be a button (this expectation will fail currently)
    // We search by role to verify accessibility
    const clearButton = screen.getByRole('button', { name: /clear/i });
    expect(clearButton).toBeInTheDocument();
  });
});
