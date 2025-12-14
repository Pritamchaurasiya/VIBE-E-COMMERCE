import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: [],
  totalQuantity: 0,
  totalAmount: 0,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addItem: (state, action) => {
      const newItem = action.payload;
      const existingItem = state.items.find(item => item.id === newItem.id);

      if (existingItem) {
        existingItem.quantity += newItem.quantity;
        existingItem.totalPrice += newItem.price * newItem.quantity;
      } else {
        state.items.push({
          id: newItem.id,
          name: newItem.name,
          price: newItem.price,
          quantity: newItem.quantity,
          totalPrice: newItem.price * newItem.quantity,
          image: newItem.image,
        });
      }

      state.totalQuantity += newItem.quantity;
      state.totalAmount += newItem.price * newItem.quantity;
    },
    removeItem: (state, action) => {
      const id = action.payload;
      const existingItem = state.items.find(item => item.id === id);

      if (existingItem) {
        state.totalQuantity -= existingItem.quantity;
        state.totalAmount -= existingItem.totalPrice;
        state.items = state.items.filter(item => item.id !== id);
      }
    },
    updateQuantity: (state, action) => {
      const { id, quantity } = action.payload;
      const existingItem = state.items.find(item => item.id === id);

      if (existingItem) {
        const quantityDiff = quantity - existingItem.quantity;
        existingItem.quantity = quantity;
        existingItem.totalPrice = existingItem.price * quantity;
        state.totalQuantity += quantityDiff;
        state.totalAmount += existingItem.price * quantityDiff;
      }
    },
    clearCart: (state) => {
      state.items = [];
      state.totalQuantity = 0;
      state.totalAmount = 0;
    },
    setCartLoading: (state) => {
      state.status = 'loading';
    },
    setCartSucceeded: (state) => {
      state.status = 'succeeded';
    },
    setCartFailed: (state, action) => {
      state.status = 'failed';
      state.error = action.payload;
    },
  },
});

export const {
  addItem,
  removeItem,
  updateQuantity,
  clearCart,
  setCartLoading,
  setCartSucceeded,
  setCartFailed,
} = cartSlice.actions;

export default cartSlice.reducer;

// Selectors
export const selectCartItems = (state) => state.cart.items;
export const selectCartTotalQuantity = (state) => state.cart.totalQuantity;
export const selectCartTotalAmount = (state) => state.cart.totalAmount;
export const selectCartStatus = (state) => state.cart.status;
export const selectCartError = (state) => state.cart.error;