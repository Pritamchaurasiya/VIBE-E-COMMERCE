import api from "./api";

const agriService = {
  // Farms
  getFarms: () => api.get("/api/v1/farms/"),
  addFarm: (data) => api.post("/api/v1/farms/", data),
  getFarm: (id) => api.get(`/api/v1/farms/${id}/`),
  updateFarm: (id, data) => api.put(`/api/v1/farms/${id}/`, data),
  deleteFarm: (id) => api.delete(`/api/v1/farms/${id}/`),

  // Soil Health
  getSoilReports: () => api.get("/api/v1/soil-health/"),
  addSoilReport: (data) => api.post("/api/v1/soil-health/", data),
  getSoilReport: (id) => api.get(`/api/v1/soil-health/${id}/`),

  // Mandi Prices
  getMandiPrices: (params) => api.get("/api/v1/mandi-prices/", { params }),
  getPriceTrends: (market, commodity) =>
    api.get("/api/v1/mandi-prices/trends/", { params: { market, commodity } }),

  // Weather
  getWeather: () => api.get("/api/v1/weather/"),

  // Advisory
  getAdvisory: (params) => api.get("/api/v1/advisory/", { params }),
  askQuestion: (data) => api.post("/api/v1/advisory/", data),
  getQuestion: (id) => api.get(`/api/v1/advisory/${id}/`),
};

export default agriService;
