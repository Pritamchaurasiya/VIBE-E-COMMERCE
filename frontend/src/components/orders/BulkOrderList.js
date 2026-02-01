import React, { useState, useEffect } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, CircularProgress } from '@mui/material';
import api from '../../services/api';

const BulkOrderList = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/api/v1/bulk-orders/');
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching bulk orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'processing': return 'info';
      case 'completed': return 'success';
      default: return 'default';
    }
  };

  if (loading) return <Container sx={{ py: 4, textAlign: 'center' }}><CircularProgress /></Container>;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>My Bulk Orders</Typography>
      {orders.length === 0 ? (
        <Typography>No bulk orders found.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Requested Price</TableCell>
                <TableCell>Approved Price</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>#{order.id}</TableCell>
                  <TableCell>{order.product?.name || 'Unknown'}</TableCell>
                  <TableCell>{order.quantity}</TableCell>
                  <TableCell>₹{order.requested_price}</TableCell>
                  <TableCell>{order.approved_price ? `₹${order.approved_price}` : '-'}</TableCell>
                  <TableCell>
                    <Chip label={order.status.toUpperCase()} color={getStatusColor(order.status)} size="small" />
                  </TableCell>
                  <TableCell>{new Date(order.created_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default BulkOrderList;
