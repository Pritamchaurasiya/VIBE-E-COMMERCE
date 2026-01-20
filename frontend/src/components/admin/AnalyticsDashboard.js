import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  Users, ShoppingBag, DollarSign, TrendingUp, Activity,
  Package, Truck, UserCheck, AlertCircle
} from 'lucide-react';
import './AnalyticsDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const AnalyticsDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      // Using the existing endpoint, assuming user is Admin
      const response = await fetch('/api/v1/admin/dashboard-stats/', {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading-spinner">Loading Analytics...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;
  if (!dashboardData) return null;

  const { revenue, orders, products, users, top_products } = dashboardData;

  // Mock data for charts since the current API might return summary only
  // In a real implementation, you would fetch time-series data
  const revenueData = [
    { name: 'Week 1', revenue: revenue.monthly * 0.2 },
    { name: 'Week 2', revenue: revenue.monthly * 0.25 },
    { name: 'Week 3', revenue: revenue.monthly * 0.22 },
    { name: 'Week 4', revenue: revenue.monthly * 0.33 },
  ];

  const orderStatusData = [
    { name: 'Pending', value: orders.pending },
    { name: 'Processing', value: orders.processing },
    { name: 'Shipped', value: orders.shipped },
    { name: 'Delivered', value: orders.delivered },
    { name: 'Cancelled', value: orders.cancelled },
  ];

  return (
    <div className="analytics-dashboard">
      <header className="dashboard-header">
        <h1>Platform Analytics</h1>
        <div className="time-range-selector">
          <button className={timeRange === '7d' ? 'active' : ''} onClick={() => setTimeRange('7d')}>7 Days</button>
          <button className={timeRange === '30d' ? 'active' : ''} onClick={() => setTimeRange('30d')}>30 Days</button>
          <button className={timeRange === '90d' ? 'active' : ''} onClick={() => setTimeRange('90d')}>3 Months</button>
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card revenue">
          <div className="stat-icon"><DollarSign size={24} /></div>
          <div className="stat-info">
            <h3>Total Revenue</h3>
            <p className="stat-value">₹{revenue.total.toLocaleString()}</p>
            <span className="stat-change positive">+12.5% vs last month</span>
          </div>
        </div>

        <div className="stat-card orders">
          <div className="stat-icon"><ShoppingBag size={24} /></div>
          <div className="stat-info">
            <h3>Total Orders</h3>
            <p className="stat-value">{orders.total.toLocaleString()}</p>
            <span className="stat-change positive">+8.2% vs last month</span>
          </div>
        </div>

        <div className="stat-card users">
          <div className="stat-icon"><Users size={24} /></div>
          <div className="stat-info">
            <h3>Total Users</h3>
            <p className="stat-value">{users.total.toLocaleString()}</p>
            <span className="stat-change positive">+5.1% vs last month</span>
          </div>
        </div>

        <div className="stat-card products">
          <div className="stat-icon"><Package size={24} /></div>
          <div className="stat-info">
            <h3>Active Products</h3>
            <p className="stat-value">{products.active.toLocaleString()}</p>
            <span className="stat-change neutral">0% vs last month</span>
          </div>
        </div>
      </div>

      <div className="charts-container">
        <div className="chart-card revenue-chart">
          <h3>Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']} />
              <Area type="monotone" dataKey="revenue" stroke="#8884d8" fill="#8884d8" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card order-status-chart">
          <h3>Order Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={orderStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {orderStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="detailed-stats">
        <div className="chart-card top-products">
          <h3>Top Selling Products</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={top_products} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="product__name" type="category" width={150} />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_sold" fill="#82ca9d" name="Units Sold" />
              <Bar dataKey="revenue" fill="#8884d8" name="Revenue" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
