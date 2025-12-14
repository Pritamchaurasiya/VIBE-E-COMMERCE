import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/products/`, { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchProductById = createAsyncThunk(
  'products/fetchProductById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/products/${id}/`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchRecommendedProducts = createAsyncThunk(
  'products/fetchRecommendedProducts',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/recommendations/?user_id=${userId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const initialState = {
  items: [],
  currentProduct: null,
  recommendedProducts: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
  filters: {
    category: '',
    priceRange: [0, 1000],
    rating: 0,
    searchQuery: '',
  },
};

const productSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        category: '',
        priceRange: [0, 1000],
        rating: 0,
        searchQuery: '',
      };
    },
    clearProductState: (state) => {
      state.currentProduct = null;
      state.status = 'idle';
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      .addCase(fetchProductById.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchProductById.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.currentProduct = action.payload;
      })
      .addCase(fetchProductById.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      .addCase(fetchRecommendedProducts.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchRecommendedProducts.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.recommendedProducts = action.payload;
      })
      .addCase(fetchRecommendedProducts.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  },
});

export const { setFilters, clearFilters, clearProductState } = productSlice.actions;

export default productSlice.reducer;

// Selectors
export const selectAllProducts = (state) => state.products.items;
export const selectCurrentProduct = (state) => state.products.currentProduct;
export const selectRecommendedProducts = (state) => state.products.recommendedProducts;
export const selectProductStatus = (state) => state.products.status;
export const selectProductError = (state) => state.products.error;
export const selectProductFilters = (state) => state.products.filters;

export const selectFilteredProducts = (state) => {
  const { items, filters } = state.products;
  return items.filter(product => {
    const matchesCategory = filters.category ? product.category === filters.category : true;
    const matchesPrice = product.price >= filters.priceRange[0] && product.price <= filters.priceRange[1];
    const matchesRating = product.rating >= filters.rating;
    const matchesSearch = product.name.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
                         product.description.toLowerCase().includes(filters.searchQuery.toLowerCase());
    return matchesCategory && matchesPrice && matchesRating && matchesSearch;
  });
};