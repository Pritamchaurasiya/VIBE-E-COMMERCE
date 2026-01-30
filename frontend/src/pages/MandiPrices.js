import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  CircularProgress,
  InputAdornment,
} from "@mui/material";
import { Search, TrendingUp, TrendingDown } from "@mui/icons-material";
import agriService from "../services/agriService";

const MandiPrices = () => {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    state: "",
    commodity: "",
    market: "",
  });

  const states = ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Maharashtra"];
  const commodities = ["Wheat", "Rice", "Cotton", "Maize", "Soybean", "Potato", "Onion"];

  useEffect(() => {
    fetchPrices();
  }, [filters]);

  const fetchPrices = async () => {
    setLoading(true);
    try {
      const response = await agriService.getMandiPrices({
        state: filters.state,
        commodity: filters.commodity,
        search: filters.market,
      });
      setPrices(response.data.results || response.data);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch prices", err);
      setLoading(false);
    }
  };

  const getTrendIcon = (current, previous) => {
    if (!previous) return null;
    return current > previous ?
      <TrendingUp color="success" fontSize="small" /> :
      <TrendingDown color="error" fontSize="small" />;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ color: "#1a237e", fontWeight: "bold" }}>
        Mandi Market Prices
      </Typography>

      <Paper sx={{ p: 3, mb: 3, bgcolor: "#f8f9fa" }}>
        <Box display="flex" gap={2} flexWrap="wrap">
          <TextField
            select
            label="State"
            value={filters.state}
            onChange={(e) => setFilters({ ...filters, state: e.target.value })}
            sx={{ minWidth: 200 }}
            size="small"
          >
            <MenuItem value="">All States</MenuItem>
            {states.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
          </TextField>

          <TextField
            select
            label="Commodity"
            value={filters.commodity}
            onChange={(e) => setFilters({ ...filters, commodity: e.target.value })}
            sx={{ minWidth: 200 }}
            size="small"
          >
            <MenuItem value="">All Commodities</MenuItem>
            {commodities.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
          </TextField>

          <TextField
            label="Search Market"
            value={filters.market}
            onChange={(e) => setFilters({ ...filters, market: e.target.value })}
            sx={{ flexGrow: 1 }}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Box>
      </Paper>

      <TableContainer component={Paper} elevation={2}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead sx={{ bgcolor: "#e8eaf6" }}>
            <TableRow>
              <TableCell sx={{ fontWeight: "bold" }}>Date</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>State</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>Market</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>Commodity</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>Variety</TableCell>
              <TableCell align="right" sx={{ fontWeight: "bold" }}>Min Price (₹)</TableCell>
              <TableCell align="right" sx={{ fontWeight: "bold" }}>Max Price (₹)</TableCell>
              <TableCell align="right" sx={{ fontWeight: "bold" }}>Modal Price (₹)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 5 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : prices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 5 }}>
                  No price data available for selected filters.
                </TableCell>
              </TableRow>
            ) : (
              prices.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.arrival_date}</TableCell>
                  <TableCell>{row.state}</TableCell>
                  <TableCell>{row.market}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {row.commodity}
                    </Box>
                  </TableCell>
                  <TableCell>{row.variety || "-"}</TableCell>
                  <TableCell align="right">{row.min_price}</TableCell>
                  <TableCell align="right">{row.max_price}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: "bold", color: "#2e7d32" }}>
                    {row.modal_price}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default MandiPrices;
