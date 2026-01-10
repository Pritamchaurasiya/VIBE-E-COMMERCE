/**
 * Formats a number as INR currency (₹).
 * @param {number} amount - The amount to format.
 * @returns {string} - The formatted currency string.
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};
