/* global globalThis */
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("authToken");
      globalThis.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const productsAPI = {
  getProducts: (params) => api.get("/api/v1/products/", { params }),
  getProduct: (slug) => api.get(`/api/v1/products/${slug}/`),
  getCategories: () => api.get("/api/v1/categories/"),
  getVendors: () => api.get("/api/v1/vendors/"),
  searchSuggestions: (query) =>
    api.get("/api/v1/search/", { params: { q: query } }),
  getRecommendations: (productId) =>
    api.get(`/api/v1/recommendations/${productId}/`),
  // New Advanced APIs
  getTrending: (days = 7, limit = 10) =>
    api.get("/api/v1/trending/", { params: { days, limit } }),
  advancedSearch: (params) => api.get("/api/v1/advanced-search/", { params }),
};

export const cartAPI = {
  getCart: () => api.get("/api/v1/cart/"),
  addToCart: (productId, quantity = 1) =>
    api.post("/api/v1/cart/", {
      product_id: productId,
      quantity,
      action: "add",
    }),
  updateCart: (productId, quantity) =>
    api.post("/api/v1/cart/", {
      product_id: productId,
      quantity,
      action: "update",
    }),
  removeFromCart: (productId) =>
    api.post("/api/v1/cart/", { product_id: productId, action: "remove" }),
  clearCart: () => api.delete("/api/v1/cart/"),
};

export const wishlistAPI = {
  getWishlist: () => api.get("/api/v1/wishlist/"),
  addToWishlist: (productId) =>
    api.post("/api/v1/wishlist/", { product_id: productId }),
  removeFromWishlist: (productId) =>
    api.delete(`/api/v1/wishlist/${productId}/`),
};

export const authAPI = {
  login: (credentials) => api.post("/api/v1/auth/login/", credentials),
  register: (userData) => api.post("/api/v1/auth/register/", userData),
  logout: () => api.post("/api/v1/auth/logout/"),
  getProfile: () => api.get("/api/v1/profile/"),
  updateProfile: (profileData) => api.put("/api/v1/profile/", profileData),
};

export const ordersAPI = {
  getOrders: () => api.get("/api/v1/orders/"),
  getOrder: (orderId) => api.get(`/api/v1/orders/${orderId}/`),
  createOrder: (orderData) => api.post("/api/start_order/", orderData),
};

export const reviewsAPI = {
  getReviews: (productSlug) =>
    api.get(`/api/v1/products/${productSlug}/reviews/`),
  createReview: (productSlug, reviewData) =>
    api.post(`/api/v1/products/${productSlug}/reviews/`, reviewData),
};

export const couponsAPI = {
  applyCoupon: (code, cartTotal) =>
    api.post("/api/v1/apply-coupon/", { code, cart_total: cartTotal }),
};

// New Flash Sales API
export const flashSalesAPI = {
  getFlashSales: () => api.get("/api/v1/flash-sales/"),
  getFlashSale: (slug) => api.get(`/api/v1/flash-sales/${slug}/`),
};

// New Deals API
export const dealsAPI = {
  getDeals: () => api.get("/api/v1/deals/"),
  getDeal: (slug) => api.get(`/api/v1/deals/${slug}/`),
};

// New Notifications API
export const notificationsAPI = {
  getNotifications: () => api.get("/api/v1/notifications/"),
  markAsRead: (notificationIds) =>
    api.post("/api/v1/notifications/", { notification_ids: notificationIds }),
  markAllAsRead: () => api.post("/api/v1/notifications/", { mark_all: true }),
};

// New Bulk Orders API
export const bulkOrdersAPI = {
  getBulkOrders: () => api.get("/api/v1/bulk-orders/"),
  createBulkOrder: (orderData) => api.post("/api/v1/bulk-orders/", orderData),
};

// New Recently Viewed API
export const recentlyViewedAPI = {
  getRecentlyViewed: (limit = 10) =>
    api.get("/api/v1/recently-viewed/", { params: { limit } }),
  addToRecentlyViewed: (productId) =>
    api.post("/api/v1/recently-viewed/", { product_id: productId }),
};

// New Vendor API
export const vendorAPI = {
  getInventory: () => api.get("/api/v1/inventory/"),
  updateStock: (productId, quantity, notes = "") =>
    api.put("/api/v1/inventory/", { product_id: productId, quantity, notes }),
  bulkUpdateInventory: (updates) =>
    api.post("/api/v1/inventory/bulk-update/", { updates }),
  getAnalytics: () => api.get("/api/v1/vendor/analytics/"),
};

// Admin Dashboard API
export const adminAPI = {
  getDashboardStats: () => api.get("/api/v1/admin/dashboard-stats/"),
  exportData: (type, params = {}) =>
    api.get("/api/v1/export/", { params: { type, ...params } }),
};

// Product Comparison API
export const compareAPI = {
  compareProducts: (productIds) =>
    api.get("/api/v1/compare/", { params: { ids: productIds.join(",") } }),
};

// Invoice API
export const invoiceAPI = {
  getInvoice: (orderId) => api.get(`/api/v1/orders/${orderId}/invoice/`),
};

// Activity API
export const activityAPI = {
  getActivity: (limit = 20) =>
    api.get("/api/v1/activity/", { params: { limit } }),
  logActivity: (type, action, data = {}) =>
    api.post("/api/v1/activity/", { type, action, data }),
};

// Health Check API
export const healthAPI = {
  check: () => api.get("/api/v1/health/"),
};

// Contact Form API
export const contactAPI = {
  submit: (name, email, message) =>
    api.post("/api/v1/contact/", { name, email, message }),
};

// Newsletter Subscription API
export const subscriptionAPI = {
  subscribe: (email) => api.post("/api/v1/subscribe/", { email }),
};

// ============================================
// AGRIM-STYLE API ENDPOINTS
// ============================================

// Crops API
export const cropsAPI = {
  getAll: () => api.get("/api/v1/crops/"),
  getProducts: (cropSlug) => api.get(`/api/v1/crops/${cropSlug}/products/`),
};

// Diseases API
export const diseasesAPI = {
  getAll: () => api.get("/api/v1/diseases/"),
  getProducts: (diseaseSlug) =>
    api.get(`/api/v1/diseases/${diseaseSlug}/products/`),
};

// Location API
export const locationAPI = {
  detect: () => api.get("/api/v1/location/detect/"),
  getPopular: (city) =>
    api.get(`/api/v1/location/popular/${encodeURIComponent(city)}/`),
};

// Deal of the Day API
export const dealOfDayAPI = {
  get: () => api.get("/api/v1/deal-of-day/"),
};

// Price Alerts API
export const priceAlertsAPI = {
  getAll: () => api.get("/api/v1/price-alerts/"),
  create: (productId, targetPrice) =>
    api.post("/api/v1/price-alerts/", {
      product_id: productId,
      target_price: targetPrice,
    }),
};

// User Coins/Rewards API
export const coinsAPI = {
  getBalance: () => api.get("/api/v1/coins/"),
};

// High Margin Products API
export const highMarginAPI = {
  get: () => api.get("/api/v1/high-margin/"),
};

// Newly Launched Products API
export const newlyLaunchedAPI = {
  get: () => api.get("/api/v1/newly-launched/"),
};

// Extend productsAPI with AGRIM features
productsAPI.getAll = (params) => api.get("/api/v1/products/", { params });
productsAPI.search = (query) =>
  api.get("/api/v1/search/", { params: { q: query } });

// ============================================
// MONITORING & ANALYTICS API ENDPOINTS
// ============================================

// Analytics Dashboard API
export const analyticsAPI = {
  getDashboard: () => api.get("/api/analytics/dashboard/"),
  getRealTimeAnalytics: () => api.get("/api/analytics/realtime/"),
  getUserAnalyticsSummary: () => api.get("/api/analytics/summary/"),
  getUserSessions: (params) => api.get("/api/analytics/sessions/", { params }),
  getSessionDetail: (sessionId) => api.get(`/api/analytics/sessions/${sessionId}/`),
  createUserInteraction: (interactionData) =>
    api.post("/api/analytics/interactions/", interactionData),
  getBehaviorPatterns: () => api.get("/api/analytics/behavior-patterns/"),
  getUserPreferences: () => api.get("/api/analytics/preferences/"),
  createUserFeedback: (feedbackData) =>
    api.post("/api/analytics/feedback/", feedbackData),
};

// Real-time Monitoring API
export const monitoringAPI = {
  getSystemHealth: () => api.get("/api/v1/health/"),
  getDatabaseMetrics: () => api.get("/api/v1/db/analytics/"),
  getDatabaseDashboard: () => api.get("/api/v1/db/dashboard/"),
  getDashboardStats: () => api.get("/api/v1/admin/dashboard-stats/"),
};

// User Analytics API
export const userAnalyticsAPI = {
  getUserAnalytics: (userId) => api.get(`/api/analytics/users/${userId}/`),
  getUserSegments: () => api.get("/api/analytics/segments/"),
  getSegmentMembers: (segmentId) => api.get(`/api/analytics/segments/${segmentId}/members/`),
  createSegment: (segmentData) => api.post("/api/analytics/segments/", segmentData),
  updateSegment: (segmentId, segmentData) =>
    api.put(`/api/analytics/segments/${segmentId}/`, segmentData),
  deleteSegment: (segmentId) => api.delete(`/api/analytics/segments/${segmentId}/`),
  getSegmentAnalytics: (segmentId) =>
    api.get(`/api/analytics/segments/${segmentId}/analytics/`),
};

// Error Tracking API
export const errorTrackingAPI = {
  getErrors: (params) => api.get("/api/analytics/errors/", { params }),
  getErrorDetail: (errorId) => api.get(`/api/analytics/errors/${errorId}/`),
  resolveError: (errorId) => api.post(`/api/analytics/errors/${errorId}/resolve/`),
  ignoreError: (errorId) => api.post(`/api/analytics/errors/${errorId}/ignore/`),
  getErrorStats: (timeRange) =>
    api.get("/api/analytics/errors/stats/", { params: { time_range: timeRange } }),
  getErrorDistribution: () => api.get("/api/analytics/errors/distribution/"),
};

// Performance Monitoring API
export const performanceAPI = {
  getPerformanceMetrics: (timeRange) =>
    api.get("/api/analytics/performance/", { params: { time_range: timeRange } }),
  getPageLoadTimes: (params) =>
    api.get("/api/analytics/performance/page-load-times/", { params }),
  getApiResponseTimes: (params) =>
    api.get("/api/analytics/performance/api-response-times/", { params }),
  getDatabasePerformance: () => api.get("/api/analytics/performance/database/"),
  getSystemMetrics: () => api.get("/api/analytics/performance/system/"),
};

// Business Intelligence API
export const businessIntelligenceAPI = {
  getKPIs: () => api.get("/api/analytics/kpis/"),
  getRevenueAnalytics: (params) =>
    api.get("/api/analytics/revenue/", { params }),
  getConversionFunnel: (params) =>
    api.get("/api/analytics/conversion-funnel/", { params }),
  getCohortAnalysis: (params) =>
    api.get("/api/analytics/cohort-analysis/", { params }),
  getCustomerLifetimeValue: (params) =>
    api.get("/api/analytics/customer-ltv/", { params }),
  getChurnAnalysis: (params) =>
    api.get("/api/analytics/churn-analysis/", { params }),
};

// ============================================
// AGRI-INTELLIGENCE API ENDPOINTS
// ============================================

export const rentalsAPI = {
  getEquipment: (params) => api.get("/api/v1/equipment/", { params }),
  getEquipmentDetail: (slug) => api.get(`/api/v1/equipment/${slug}/`),
  getBookings: () => api.get("/api/v1/rentals/"),
  bookEquipment: (bookingData) => api.post("/api/v1/rentals/book/", bookingData),
};

export const schemesAPI = {
  getSchemes: (params) => api.get("/api/v1/schemes/", { params }),
};

export const forumAPI = {
  getPosts: (params) => api.get("/api/v1/forum/posts/", { params }),
  getPostDetail: (id) => api.get(`/api/v1/forum/posts/${id}/`),
  createPost: (postData) => api.post("/api/v1/forum/posts/", postData),
  addComment: (postId, commentData) =>
    api.post(`/api/v1/forum/posts/${postId}/comments/`, commentData),
};

// Export all APIs
export default api;
