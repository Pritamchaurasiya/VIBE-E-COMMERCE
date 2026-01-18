import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  TrendingUp,
  ShoppingCart,
  Inventory,
  AttachMoney,
  Star
} from '@mui/icons-material';
import axios from 'axios';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const VendorDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/v1/vendor/analytics/');
        setData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching analytics:', err);
        // Fallback for demo if API fails or needs authentication not yet active
        // Ideally handled by error boundary or redirect to login
        if (err.response && (err.response.status === 401 || err.response.status === 403)) {
             setError("Access Denied. You must be logged in as a Vendor.");
        } else {
             setError('Failed to load dashboard data.');
        }
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, height: '80vh', alignItems: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!data) return null;

  const { overview, revenue, orders, reviews, top_products } = data;

  // Prepare chart data
  const revenueData = [
    { name: 'Weekly', amount: revenue.weekly },
    { name: 'Monthly', amount: revenue.monthly },
    { name: 'Total', amount: revenue.total },
  ];

  const productStatusData = [
    { name: 'Active', value: overview.active_products },
    { name: 'Out of Stock', value: overview.out_of_stock },
    { name: 'Low Stock', value: overview.low_stock },
  ];

  const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Vendor Dashboard
        </Typography>
        <Typography color="textSecondary">
          Overview of your store's performance
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Revenue"
            value={`₹${revenue.total}`}
            icon={<AttachMoney />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Orders"
            value={orders.total}
            icon={<ShoppingCart />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Products"
            value={overview.total_products}
            icon={<Inventory />}
            color="warning.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Average Rating"
            value={reviews.average_rating}
            icon={<Star />}
            color="secondary.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Revenue Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Overview
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `₹${value}`} />
                <Bar dataKey="amount" fill="#8884d8" name="Revenue" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Product Status Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Inventory Status
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={productStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {productStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Top Selling Products */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            <Box sx={{ p: 2, bgcolor: 'background.neutral' }}>
              <Typography variant="h6">Top Selling Products</Typography>
            </Box>
            <Divider />
            <List>
              {top_products.map((product, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.light' }}>
                        {index + 1}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={product.product__name}
                      secondary={`Sold: ${product.total_sold} units`}
                    />
                    <Chip
                      label="Top Seller"
                      color="primary"
                      size="small"
                      icon={<TrendingUp />}
                    />
                  </ListItem>
                  {index < top_products.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
              {top_products.length === 0 && (
                <ListItem>
                  <ListItemText primary="No sales data available yet." />
                </ListItem>
              )}
            </List>
          </Paper>
        </Grid>

        {/* Recent Actions / Quick Stats */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Pending Actions
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Pending Bulk Orders"
                  secondary={`${orders.pending_bulk_orders} orders waiting for approval`}
                />
                <Button variant="outlined" size="small">View</Button>
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemText
                  primary="Low Stock Alerts"
                  secondary={`${overview.low_stock} products below threshold`}
                />
                <Button variant="outlined" size="small" color="warning">Update Stock</Button>
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemText
                  primary="Out of Stock"
                  secondary={`${overview.out_of_stock} products unavailable`}
                />
                <Button variant="outlined" size="small" color="error">Restock</Button>
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default VendorDashboard;
