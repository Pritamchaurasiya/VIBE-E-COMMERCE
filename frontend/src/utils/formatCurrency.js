/**
 * Formats a number as Indian Rupees (INR)
 * @param {number} amount - The amount to format
 * @param {boolean} showSymbol - Whether to show the currency symbol (defaults to true)
 * @returns {string} The formatted string
 */
export const formatCurrency = (amount, showSymbol = true) => {
  if (amount === undefined || amount === null) {
    return "";
  }

  try {
    const formatter = new Intl.NumberFormat('en-IN', {
      style: showSymbol ? 'currency' : 'decimal',
      currency: 'INR',
      maximumFractionDigits: 0,
      minimumFractionDigits: 0,
    });

    return formatter.format(amount);
  } catch (error) {
    console.error("Error formatting currency:", error);
    return showSymbol ? `₹${amount}` : `${amount}`;
  }
};

export default formatCurrency;
