
/**
 * Formats a number as a currency string (e.g., ₹1,200)
 * Uses 'en-IN' locale and 'INR' currency.
 *
 * @param {number|string} amount - The amount to format
 * @returns {string} The formatted currency string
 */
export const formatCurrency = (amount) => {
  const numericAmount = typeof amount === 'string' ? parseFloat(amount) : amount;

  if (isNaN(numericAmount) || numericAmount === null || numericAmount === undefined) {
    return '₹0';
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(numericAmount);
};
