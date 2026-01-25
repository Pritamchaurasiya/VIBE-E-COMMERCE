import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Import reducers
import cartReducer from './features/cart/cartSlice';
import themeReducer from './features/theme/themeSlice';
import authReducer from './features/auth/authSlice';
import productReducer from './features/products/productSlice';

// Combine reducers
const rootReducer = combineReducers({
  cart: cartReducer,
  theme: themeReducer,
  auth: authReducer,
  products: productReducer,
});

// Redux persist configuration
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['cart', 'theme', 'auth'], // Only persist these reducers
};

// Create persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

// Create persistor
export const persistor = persistStore(store);