import { formatCurrency } from './formatCurrency';

describe('formatCurrency', () => {
  test('formats number to INR currency', () => {
    expect(formatCurrency(100)).toBe('₹100');
    expect(formatCurrency(1234)).toBe('₹1,234');
    expect(formatCurrency(1234567)).toBe('₹12,34,567');
  });

  test('handles zero', () => {
    expect(formatCurrency(0)).toBe('₹0');
  });
});
