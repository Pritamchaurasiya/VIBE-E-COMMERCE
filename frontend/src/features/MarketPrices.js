import React, { useState, useEffect } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, CircularProgress, Container } from '@mui/material';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import axios from 'axios';

const MarketPrices = () => {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await axios.get('/api/v1/market/prices/');
        setPrices(response.data.results || response.data);
      } catch (err) {
        console.error('Failed to fetch market prices');
      } finally {
        setLoading(false);
      }
    };
    fetchPrices();
  }, []);

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp color="success" />;
    if (trend === 'down') return <TrendingDown color="error" />;
    return <Remove color="disabled" />;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: '#1976d2', mb: 3 }}>
        Live Market Prices (Mandi Rates)
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
            <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper} elevation={3}>
            <Table>
            <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Crop</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Market (Mandi)</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Location</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold' }}>Price (₹/Quintal)</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold' }}>Trend</TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold' }}>Date</TableCell>
                </TableRow>
            </TableHead>
            <TableBody>
                {prices.length > 0 ? (
                    prices.map((item) => (
                    <TableRow key={item.id} hover>
                        <TableCell sx={{ fontWeight: '500' }}>{item.crop_name}</TableCell>
                        <TableCell>{item.market_name}</TableCell>
                        <TableCell>{item.location}</TableCell>
                        <TableCell align="right" sx={{ color: 'success.main', fontWeight: 'bold' }}>₹{item.price}</TableCell>
                        <TableCell align="center">{getTrendIcon(item.trend)}</TableCell>
                        <TableCell align="right">{item.date}</TableCell>
                    </TableRow>
                    ))
                ) : (
                    <TableRow>
                        <TableCell colSpan={6} align="center">No market data available currently.</TableCell>
                    </TableRow>
                )}
            </TableBody>
            </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default MarketPrices;
