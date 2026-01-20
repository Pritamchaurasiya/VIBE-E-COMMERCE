import React, { useState, useEffect } from 'react';
import {
    Container, Grid, Paper, Typography, Box, Card, CardContent,
    CircularProgress, Table, TableBody, TableCell, TableHead, TableRow
} from '@mui/material';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
    ResponsiveContainer, LineChart, Line
} from 'recharts';
import { TrendingUp, ShoppingBag, Inventory, Star } from '@mui/icons-material';
import axios from 'axios';
import TopNav from '../components/layout/TopNav';
import BottomNav from '../components/layout/BottomNav';

const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
        <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                    <Typography color="textSecondary" gutterBottom variant="subtitle2">
                        {title}
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                        {value}
                    </Typography>
                </Box>
                <Box sx={{
                    bgcolor: `${color}20`,
                    p: 1.5,
                    borderRadius: '50%',
                    color: color
                }}>
                    {icon}
                </Box>
            </Box>
        </CardContent>
    </Card>
);

const VendorDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/api/v1/vendor/analytics/');
                setData(response.data);
            } catch (err) {
                // Check if 403 (not a vendor)
                if (err.response && err.response.status === 403) {
                    setError('Access Denied. You must be a registered vendor.');
                } else {
                    setError('Failed to load dashboard data.');
                }
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
            <CircularProgress />
        </Box>
    );

    if (error) return (
        <Box p={4}>
            <TopNav />
            <Container>
                <Paper sx={{ p: 4, mt: 4, textAlign: 'center' }}>
                    <Typography variant="h5" color="error">{error}</Typography>
                </Paper>
            </Container>
        </Box>
    );

    return (
        <div style={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
            <TopNav />
            <Container maxWidth="xl" sx={{ mt: 4, mb: 8 }}>
                <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ mb: 4 }}>
                    Vendor Dashboard
                </Typography>

                {/* Stats Cards */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Total Revenue"
                            value={`₹${data.revenue.total}`}
                            icon={<TrendingUp />}
                            color="#2e7d32"
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Total Orders"
                            value={data.orders.total}
                            icon={<ShoppingBag />}
                            color="#1976d2"
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Active Products"
                            value={data.overview.active_products}
                            icon={<Inventory />}
                            color="#ed6c02"
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <StatCard
                            title="Avg Rating"
                            value={data.reviews.average_rating}
                            icon={<Star />}
                            color="#9c27b0"
                        />
                    </Grid>
                </Grid>

                <Grid container spacing={3}>
                    {/* Sales Chart */}
                    <Grid item xs={12} md={8}>
                        <Paper sx={{ p: 3, borderRadius: 2, height: 400 }}>
                            <Typography variant="h6" gutterBottom>
                                Sales Trends (Last 30 Days)
                            </Typography>
                            <ResponsiveContainer width="100%" height="90%">
                                <BarChart data={data.daily_sales}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, {day: 'numeric', month: 'short'})}
                                    />
                                    <YAxis />
                                    <RechartsTooltip
                                        formatter={(value) => [`₹${value}`, 'Sales']}
                                        labelFormatter={(label) => new Date(label).toLocaleDateString()}
                                    />
                                    <Bar dataKey="sales" fill="#2e7d32" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </Paper>
                    </Grid>

                    {/* Top Products */}
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 3, borderRadius: 2, height: 400, overflow: 'auto' }}>
                            <Typography variant="h6" gutterBottom>
                                Top Selling Products
                            </Typography>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Product</TableCell>
                                        <TableCell align="right">Sold</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {data.top_products.map((product) => (
                                        <TableRow key={product.product__slug}>
                                            <TableCell>{product.product__name}</TableCell>
                                            <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                                                {product.total_sold}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {data.top_products.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={2} align="center">No sales yet</TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
            <BottomNav />
        </div>
    );
};

export default VendorDashboard;
