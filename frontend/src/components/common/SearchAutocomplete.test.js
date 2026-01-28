import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchAutocomplete from './SearchAutocomplete';

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

describe('SearchAutocomplete', () => {
  test('renders search input', () => {
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search products/i);
    expect(input).toBeInTheDocument();
  });

  test('clear button has accessible label', () => {
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search products/i);

    // Type something to make the clear button appear
    fireEvent.change(input, { target: { value: 'test' } });

    const clearButton = screen.getByLabelText('Clear search query');
    expect(clearButton).toBeInTheDocument();
    expect(clearButton.tagName).toBe('BUTTON'); // Ensure it's a button
  });
});
