import React, {
  createContext,
  useState,
  useEffect,
  useContext,
  useMemo,
  useCallback,
} from "react";
import PropTypes from "prop-types";
import { cartAPI } from "../services/api";

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({
    items: [],
    total_cost: 0,
    item_count: 0,
  });
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const loadCart = useCallback(async () => {
    try {
      const response = await cartAPI.getCart();
      setCart(response.data);
    } catch (error) {
      console.error("Failed to load cart:", error);
    }
  }, []);

  useEffect(() => {
    loadCart();
  }, [loadCart]);

  // Real-time updates with polling
  useEffect(() => {
    if (!isAuthenticated) return;

    const pollInterval = setInterval(() => {
      loadCart();
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(pollInterval);
  }, [isAuthenticated, loadCart]);

  // Listen for authentication changes
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("token");
      setIsAuthenticated(!!token);
    };

    checkAuth();
    // Using window for browser storage events - eslint globalThis rule disabled
    // eslint-disable-next-line no-restricted-globals
    window.addEventListener("storage", checkAuth);
    // eslint-disable-next-line no-restricted-globals
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  const addToCart = useCallback(async (productId, quantity = 1) => {
    setLoading(true);
    try {
      const response = await cartAPI.addToCart(productId, quantity);
      setCart(response.data);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || "Failed to add to cart",
      };
    } finally {
      setLoading(false);
    }
  }, []);

  const updateCartItem = useCallback(async (productId, quantity) => {
    setLoading(true);
    try {
      const response = await cartAPI.updateCart(productId, quantity);
      setCart(response.data);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || "Failed to update cart",
      };
    } finally {
      setLoading(false);
    }
  }, []);

  const removeFromCart = useCallback(async (productId) => {
    setLoading(true);
    try {
      const response = await cartAPI.removeFromCart(productId);
      setCart(response.data);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || "Failed to remove from cart",
      };
    } finally {
      setLoading(false);
    }
  }, []);

  const clearCart = useCallback(async () => {
    setLoading(true);
    try {
      await cartAPI.clearCart();
      setCart({
        items: [],
        total_cost: 0,
        item_count: 0,
      });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || "Failed to clear cart",
      };
    } finally {
      setLoading(false);
    }
  }, []);

  const value = useMemo(
    () => ({
      cart,
      loading,
      addToCart,
      updateCartItem,
      removeFromCart,
      clearCart,
      refreshCart: loadCart,
    }),
    [
      cart,
      loading,
      addToCart,
      updateCartItem,
      removeFromCart,
      clearCart,
      loadCart,
    ],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

CartProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
