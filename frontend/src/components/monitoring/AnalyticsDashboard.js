import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, LinearProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Tooltip, Select, MenuItem, FormControl, InputLabel, Chip
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Refresh, FilterList,
  AttachMoney, ShoppingCart, People, Inventory
} from '@mui/icons-material';
import { getAnalyticsDashboard, getRealTimeAnalytics } from '../../services/api';

const MetricCard = ({ title, value, change, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box sx={{ p: 1, borderRadius: 2, bgcolor: `${color}.light`, color: `${color}.main` }}>
          {icon}
        </Box>
        {change && (
          <Chip
            label={`${change > 0 ? '+' : ''}${change}%`}
            color={change > 0 ? 'success' : 'error'}
            size="small"
            icon={change > 0 ? <TrendingUp /> : <TrendingDown />}
          />
        )}
      </Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {title}
      </Typography>
    </CardContent>
  </Card>
);

const AnalyticsDashboard = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      // In a real app, we would fetch data here
      // const dashboardData = await getAnalyticsDashboard();
      // setData(dashboardData);

      // Mock data for demonstration
      setTimeout(() => {
        setData({
          revenue: { value: '₹12,45,000', change: 12.5 },
          orders: { value: '1,245', change: 8.2 },
          users: { value: '5,678', change: -2.4 },
          products: { value: '845', change: 0 },
          topProducts: [
            { name: 'Organic Wheat Seeds', sales: 124, revenue: '₹62,000' },
            { name: 'Nano Urea Liquid', sales: 98, revenue: '₹24,500' },
            { name: 'Solar Insect Trap', sales: 76, revenue: '₹38,000' },
            { name: 'Drip Irrigation Kit', sales: 45, revenue: '₹1,12,500' },
            { name: 'Neem Oil Pesticide', sales: 156, revenue: '₹46,800' },
          ]
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [timeRange]);

  if (loading || !data) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          Analytics Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last Quarter</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={fetchData}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Revenue"
            value={data.revenue.value}
            change={data.revenue.change}
            icon={<AttachMoney />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Orders"
            value={data.orders.value}
            change={data.orders.change}
            icon={<ShoppingCart />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Users"
            value={data.users.value}
            change={data.users.change}
            icon={<People />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Products"
            value={data.products.value}
            change={data.products.change}
            icon={<Inventory />}
            color="info"
          />
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Top Selling Products
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Product Name</TableCell>
                      <TableCell align="right">Sales Volume</TableCell>
                      <TableCell align="right">Revenue</TableCell>
                      <TableCell align="right">Trend</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.topProducts.map((product) => (
                      <TableRow key={product.name}>
                        <TableCell component="th" scope="row">
                          {product.name}
                        </TableCell>
                        <TableCell align="right">{product.sales}</TableCell>
                        <TableCell align="right">{product.revenue}</TableCell>
                        <TableCell align="right">
                          <Box sx={{ width: 100, display: 'inline-block' }}>
                            <LinearProgress variant="determinate" value={Math.random() * 100} sx={{ height: 6, borderRadius: 3 }} />
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Traffic Source
              </Typography>
              <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Organic Search</Typography>
                    <Typography variant="body2" fontWeight="bold">45%</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={45} color="primary" />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Direct</Typography>
                    <Typography variant="body2" fontWeight="bold">25%</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={25} color="success" />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Social Media</Typography>
                    <Typography variant="body2" fontWeight="bold">20%</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={20} color="warning" />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Referral</Typography>
                    <Typography variant="body2" fontWeight="bold">10%</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={10} color="info" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;
