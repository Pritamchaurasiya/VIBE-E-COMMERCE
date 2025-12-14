import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box, Typography, Grid, Paper, Card, CardContent, CardHeader, Avatar,
  List, ListItem, ListItemAvatar, ListItemText, Divider, Chip, Tabs, Tab,
  TextField, Button, CircularProgress, Alert, useTheme, IconButton, Tooltip
} from '@mui/material';
import {
  ShoppingCart, AttachMoney, People, Inventory, Assessment, Notifications,
  Dashboard, ShoppingBag, TrendingUp, TrendingDown, Warning, CheckCircle,
  Schedule, BarChart, PieChart, Timeline, Settings, Security, Speed, Storage
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../utils/AuthContext';
import { usePerformanceMonitor } from '../../utils/performanceUtils';
import { AnimatedCounter, StaggeredList } from '../common/AdvancedAnimations';

const EnhancedAdminDashboard = () => {
  const theme = useTheme();
  const { isAuthenticated, user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState('today');
  const [notifications, setNotifications] = useState([]);
  const [performanceIssues, setPerformanceIssues] = useState([]);

  // Mock WebSocket connection for real-time updates
  const { lastMessage, sendMessage } = useWebSocket(
    process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/admin/',
    { reconnect: true }
  );

  // Performance monitoring
  const { issues } = usePerformanceMonitor((issue) => {
    setPerformanceIssues(prev => [...prev, issue]);
  });

  // Mock data - in a real app, this would come from API
  const [dashboardData, setDashboardData] = useState({
    sales: {
      today: 0,
      thisWeek: 0,
      thisMonth: 0,
      total: 0,
      trend: 'up',
      trendValue: 0
    },
    orders: {
      today: 0,
      pending: 0,
      completed: 0,
      cancelled: 0,
      trend: 'up',
      trendValue: 0
    },
    customers: {
      active: 0,
      new: 0,
      churned: 0,
      total: 0,
      trend: 'up',
      trendValue: 0
    },
    products: {
      total: 0,
      lowStock: 0,
      outOfStock: 0,
      featured: 0
    },
    revenue: {
      today: 0,
      thisWeek: 0,
      thisMonth: 0,
      total: 0,
      avgOrderValue: 0
    },
    recentOrders: [],
    topProducts: [],
    customerActivity: []
  });

  // Simulate data loading
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Mock data
        const mockData = {
          sales: {
            today: 42,
            thisWeek: 210,
            thisMonth: 840,
            total: 12500,
            trend: 'up',
            trendValue: 12.5
          },
          orders: {
            today: 18,
            pending: 3,
            completed: 15,
            cancelled: 2,
            trend: 'up',
            trendValue: 8.3
          },
          customers: {
            active: 1250,
            new: 42,
            churned: 18,
            total: 5800,
            trend: 'up',
            trendValue: 5.2
          },
          products: {
            total: 3200,
            lowStock: 45,
            outOfStock: 8,
            featured: 120
          },
          revenue: {
            today: 12500,
            thisWeek: 62500,
            thisMonth: 250000,
            total: 12500000,
            avgOrderValue: 1250
          },
          recentOrders: [
            {
              id: 'ORD12345',
              customer: 'John Doe',
              amount: 2500,
              status: 'completed',
              date: '2023-12-12T10:30:00',
              items: 3
            },
            {
              id: 'ORD12346',
              customer: 'Jane Smith',
              amount: 1500,
              status: 'processing',
              date: '2023-12-12T09:45:00',
              items: 2
            },
            {
              id: 'ORD12347',
              customer: 'Bob Johnson',
              amount: 3500,
              status: 'shipped',
              date: '2023-12-12T08:15:00',
              items: 5
            }
          ],
          topProducts: [
            { id: 'PROD001', name: 'Premium Organic Fertilizer', sales: 125, revenue: 25000 },
            { id: 'PROD002', name: 'Advanced Pest Control', sales: 98, revenue: 19600 },
            { id: 'PROD003', name: 'High-Yield Seeds', sales: 85, revenue: 17000 }
          ],
          customerActivity: [
            { id: 'CUST001', name: 'John Doe', lastActive: '5 mins ago', orders: 12, spending: 15000 },
            { id: 'CUST002', name: 'Jane Smith', lastActive: '2 hours ago', orders: 8, spending: 12000 },
            { id: 'CUST003', name: 'Bob Johnson', lastActive: '1 day ago', orders: 5, spending: 8500 }
          ]
        };

        setDashboardData(mockData);
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
        setLoading(false);
        console.error('Dashboard load error:', err);
      }
    };

    loadDashboardData();
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        setRealTimeData(data);

        // Update notifications
        if (data.type === 'order' || data.type === 'alert') {
          setNotifications(prev => [
            {
              id: Date.now().toString(),
              type: data.type,
              message: data.message,
              timestamp: new Date().toISOString(),
              read: false
            },
            ...prev
          ]);
        }
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    }
  }, [lastMessage]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };

  const markNotificationAsRead = (id) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  const getTrendIcon = (trend) => {
    return trend === 'up' ? (
      <TrendingUp color="success" fontSize="small" />
    ) : (
      <TrendingDown color="error" fontSize="small" />
    );
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      completed: { label: 'Completed', color: 'success' },
      processing: { label: 'Processing', color: 'info' },
      shipped: { label: 'Shipped', color: 'primary' },
      pending: { label: 'Pending', color: 'warning' },
      cancelled: { label: 'Cancelled', color: 'error' }
    };

    const config = statusConfig[status] || { label: status, color: 'default' };
    return <Chip label={config.label} size="small" color={config.color} />;
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  };

  if (!isAuthenticated || (user && user.role !== 'admin')) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">Access denied. Admin privileges required.</Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>Loading dashboard...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button onClick={() => window.location.reload()} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ flex: 1, overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{
        p: 3,
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Dashboard color="primary" fontSize="large" />
          <Typography variant="h4" fontWeight="bold">
            Admin Dashboard
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Search..."
            value={searchQuery}
            onChange={handleSearchChange}
            sx={{ width: 250 }}
            InputProps={{
              startAdornment: (
                <Box sx={{ mr: 1, color: 'text.secondary' }}>
                  🔍
                </Box>
              )
            }}
          />

          <Button
            variant="contained"
            startIcon={<Notifications />}
            sx={{ position: 'relative' }}
          >
            Notifications
            {notifications.filter(n => !n.read).length > 0 && (
              <Box sx={{
                position: 'absolute',
                top: -8,
                right: -8,
                width: 20,
                height: 20,
                bgcolor: 'error.main',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '0.7rem',
                fontWeight: 'bold'
              }}>
                {notifications.filter(n => !n.read).length}
              </Box>
            )}
          </Button>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ p: 3, overflowY: 'auto', height: 'calc(100vh - 120px)' }}>
        {/* Summary Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Sales Card */}
            <Grid item xs={12} sm={6} md={3}>
              <motion.div variants={itemVariants}>
                <Card sx={{ height: '100%', borderLeft: `4px solid ${theme.palette.success.main}` }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle2" color="text.secondary" fontWeight="medium">
                        TODAY'S SALES
                      </Typography>
                      <ShoppingCart color="success" />
                    </Box>
                    <Typography variant="h3" fontWeight="bold" color="success.main">
                      <AnimatedCounter from={0} to={dashboardData.sales.today} />
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      {getTrendIcon(dashboardData.sales.trend)}
                      <Typography variant="body2" color={dashboardData.sales.trend === 'up' ? 'success.main' : 'error.main'}>
                        {dashboardData.sales.trendValue}% vs last period
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Revenue Card */}
            <Grid item xs={12} sm={6} md={3}>
              <motion.div variants={itemVariants}>
                <Card sx={{ height: '100%', borderLeft: `4px solid ${theme.palette.primary.main}` }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle2" color="text.secondary" fontWeight="medium">
                        TODAY'S REVENUE
                      </Typography>
                      <AttachMoney color="primary" />
                    </Box>
                    <Typography variant="h3" fontWeight="bold" color="primary.main">
                      ₹<AnimatedCounter from={0} to={dashboardData.revenue.today} suffix="K" />
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      {getTrendIcon(dashboardData.sales.trend)}
                      <Typography variant="body2" color={dashboardData.sales.trend === 'up' ? 'success.main' : 'error.main'}>
                        {dashboardData.sales.trendValue}% vs last period
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Orders Card */}
            <Grid item xs={12} sm={6} md={3}>
              <motion.div variants={itemVariants}>
                <Card sx={{ height: '100%', borderLeft: `4px solid ${theme.palette.info.main}` }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle2" color="text.secondary" fontWeight="medium">
                        TODAY'S ORDERS
                      </Typography>
                      <ShoppingBag color="info" />
                    </Box>
                    <Typography variant="h3" fontWeight="bold" color="info.main">
                      <AnimatedCounter from={0} to={dashboardData.orders.today} />
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      {getTrendIcon(dashboardData.orders.trend)}
                      <Typography variant="body2" color={dashboardData.orders.trend === 'up' ? 'success.main' : 'error.main'}>
                        {dashboardData.orders.trendValue}% vs last period
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Customers Card */}
            <Grid item xs={12} sm={6} md={3}>
              <motion.div variants={itemVariants}>
                <Card sx={{ height: '100%', borderLeft: `4px solid ${theme.palette.warning.main}` }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle2" color="text.secondary" fontWeight="medium">
                        NEW CUSTOMERS
                      </Typography>
                      <People color="warning" />
                    </Box>
                    <Typography variant="h3" fontWeight="bold" color="warning.main">
                      <AnimatedCounter from={0} to={dashboardData.customers.new} />
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      {getTrendIcon(dashboardData.customers.trend)}
                      <Typography variant="body2" color={dashboardData.customers.trend === 'up' ? 'success.main' : 'error.main'}>
                        {dashboardData.customers.trendValue}% vs last period
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>

          {/* Quick Stats */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title="Inventory Status"
                  titleTypographyProps={{ variant: 'h6', fontWeight: 'bold' }}
                  avatar={<Inventory color="primary" />}
                />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Total Products</Typography>
                        <Typography variant="body1" fontWeight="bold">{dashboardData.products.total}</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Featured Products</Typography>
                        <Typography variant="body1" fontWeight="bold">{dashboardData.products.featured}</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Low Stock</Typography>
                        <Typography variant="body1" fontWeight="bold" color="warning.main">{dashboardData.products.lowStock}</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Out of Stock</Typography>
                        <Typography variant="body1" fontWeight="bold" color="error.main">{dashboardData.products.outOfStock}</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title="Order Status"
                  titleTypographyProps={{ variant: 'h6', fontWeight: 'bold' }}
                  avatar={<Assessment color="secondary" />}
                />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Completed</Typography>
                        <Typography variant="body1" fontWeight="bold" color="success.main">{dashboardData.orders.completed}</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Pending</Typography>
                        <Typography variant="body1" fontWeight="bold" color="warning.main">{dashboardData.orders.pending}</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Shipped</Typography>
                        <Typography variant="body1" fontWeight="bold" color="info.main">{dashboardData.orders.shipped || 0}</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">Cancelled</Typography>
                        <Typography variant="body1" fontWeight="bold" color="error.main">{dashboardData.orders.cancelled}</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Recent Orders */}
          <Card sx={{ mb: 4 }}>
            <CardHeader
              title="Recent Orders"
              titleTypographyProps={{ variant: 'h6', fontWeight: 'bold' }}
              avatar={<ShoppingBag color="primary" />}
              action={
                <Button size="small" variant="outlined">
                  View All Orders
                </Button>
              }
            />
            <CardContent>
              <List>
                {dashboardData.recentOrders.map((order, index) => (
                  <React.Fragment key={order.id}>
                    <ListItem
                      secondaryAction={
                        <Typography variant="body1" fontWeight="bold">
                          ₹{order.amount.toLocaleString()}
                        </Typography>
                      }
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.light' }}>
                          <ShoppingCart />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" fontWeight="medium">
                              {order.customer}
                            </Typography>
                            {getStatusChip(order.status)}
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            {new Date(order.date).toLocaleString()} • {order.items} items • Order #{order.id}
                          </Typography>
                        }
                      />
                    </ListItem>
                    {index < dashboardData.recentOrders.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Performance Monitoring Section */}
          <Card sx={{ mb: 4 }}>
            <CardHeader
              title="Performance Monitoring"
              titleTypographyProps={{ variant: 'h6', fontWeight: 'bold' }}
              avatar={<Speed color="success" />}
              action={
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<CheckCircle />}
                    disabled={performanceIssues.length === 0}
                  >
                    {performanceIssues.length} Issues
                  </Button>
                  <Button size="small" variant="outlined" startIcon={<Settings />}>
                    Configure
                  </Button>
                </Box>
              }
            />
            <CardContent>
              {performanceIssues.length > 0 ? (
                <List>
                  {performanceIssues.slice(0, 5).map((issue, index) => (
                    <React.Fragment key={issue.id}>
                      <ListItem>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: issue.severity === 'critical' ? 'error.main' : 'warning.main' }}>
                            {issue.severity === 'critical' ? <Warning /> : <Schedule />}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Typography variant="body1" fontWeight="medium">
                              {issue.type} Performance Issue
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary">
                              {issue.message || `${issue.type}: ${issue.actual} (threshold: ${issue.threshold})`}
                            </Typography>
                          }
                        />
                        <Chip
                          label={issue.severity}
                          size="small"
                          color={issue.severity === 'critical' ? 'error' : 'warning'}
                        />
                      </ListItem>
                      {index < performanceIssues.slice(0, 5).length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
                  <CheckCircle color="success" fontSize="large" />
                  <Typography variant="body1" color="text.secondary">
                    No performance issues detected. All systems are running optimally.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Real-time Notifications */}
          <Card sx={{ mb: 4 }}>
            <CardHeader
              title="Real-time Activity"
              titleTypographyProps={{ variant: 'h6', fontWeight: 'bold' }}
              avatar={<Notifications color="info" />}
            />
            <CardContent>
              {notifications.length > 0 ? (
                <List>
                  {notifications.slice(0, 5).map((notification, index) => (
                    <React.Fragment key={notification.id}>
                      <ListItem
                        onClick={() => markNotificationAsRead(notification.id)}
                        sx={{
                          cursor: 'pointer',
                          bgcolor: notification.read ? 'transparent' : 'action.hover',
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: notification.type === 'order' ? 'primary.main' : 'error.main' }}>
                            {notification.type === 'order' ? <ShoppingCart /> : <Warning />}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Typography variant="body1" fontWeight={notification.read ? 'normal' : 'medium'}>
                              {notification.message}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary">
                              {new Date(notification.timestamp).toLocaleString()}
                            </Typography>
                          }
                        />
                        {!notification.read && (
                          <Box sx={{
                            width: 8,
                            height: 8,
                            bgcolor: 'error.main',
                            borderRadius: '50%'
                          }} />
                        )}
                      </ListItem>
                      {index < notifications.slice(0, 5).length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
                  <Notifications color="action" fontSize="large" />
                  <Typography variant="body1" color="text.secondary">
                    No recent activity. All systems are quiet.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Box>
  );
};

export default EnhancedAdminDashboard;