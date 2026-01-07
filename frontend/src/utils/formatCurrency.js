/**
 * Format a number as Indian Rupee (INR) currency
 * @param {number} amount - The amount to format
 * @param {boolean} showSymbol - Whether to show the currency symbol (default: true)
 * @returns {string} - The formatted currency string
 */
export const formatCurrency = (amount, showSymbol = true) => {
  if (amount === undefined || amount === null) {
    return "";
  }

  const formatter = new Intl.NumberFormat('en-IN', {
    style: showSymbol ? 'currency' : 'decimal',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });

  return formatter.format(amount);
};

export default formatCurrency;
