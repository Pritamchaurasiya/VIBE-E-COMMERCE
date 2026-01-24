import React, { useState, useEffect } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, CircularProgress, Select, MenuItem, FormControl, InputLabel, Box } from '@mui/material';
import { mandiPricesAPI } from '../services/api';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';

const MandiPricesPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [market, setMarket] = useState('Local Mandi');

  const fetchPrices = async () => {
    setLoading(true);
    try {
      const response = await mandiPricesAPI.getPrices(market);
      setData(response.data);
    } catch (error) {
      console.error("Error fetching prices", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
  }, [market]);

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp color="success" />;
    if (trend === 'down') return <TrendingDown color="error" />;
    return <Remove color="action" />;
  };

  if (loading && !data) return <Container sx={{ py: 4, textAlign: 'center' }}><CircularProgress /></Container>;

  return (
    <Container sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">Live Mandi Prices</Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select Market</InputLabel>
          <Select
            value={market}
            label="Select Market"
            onChange={(e) => setMarket(e.target.value)}
          >
            <MenuItem value="Local Mandi">Local Mandi</MenuItem>
            <MenuItem value="Azadpur Mandi">Azadpur Mandi</MenuItem>
            <MenuItem value="Vashi Market">Vashi Market</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {data && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead sx={{ bgcolor: 'grey.100' }}>
              <TableRow>
                <TableCell><strong>Commodity</strong></TableCell>
                <TableCell align="right"><strong>Price (₹/Quintal)</strong></TableCell>
                <TableCell align="center"><strong>Trend</strong></TableCell>
                <TableCell align="center"><strong>Status</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.prices.map((item) => (
                <TableRow key={item.name}>
                  <TableCell component="th" scope="row">{item.name}</TableCell>
                  <TableCell align="right">₹{item.price}</TableCell>
                  <TableCell align="center">{getTrendIcon(item.trend)}</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={item.trend.toUpperCase()}
                      color={item.trend === 'up' ? 'success' : item.trend === 'down' ? 'error' : 'default'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Box sx={{ p: 2, textAlign: 'right' }}>
            <Typography variant="caption" color="text.secondary">
              Last Updated: {new Date(data.last_updated).toLocaleString()}
            </Typography>
          </Box>
        </TableContainer>
      )}
    </Container>
  );
};

export default MandiPricesPage;
