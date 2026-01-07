/**
 * Formats a number as Indian Rupee (INR) currency.
 * @param {number} amount - The amount to format.
 * @returns {string} - The formatted currency string (e.g., "₹400").
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
};
