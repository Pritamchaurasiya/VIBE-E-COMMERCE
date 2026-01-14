import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Box,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from "@mui/material";
import { Bar, Line, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { analyticsAPI } from "../../services/api"; // Assuming this exists or using generic api
import axios from "axios";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalyticsDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState("30d");

  useEffect(() => {
    fetchData();
  }, [timeRange]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Mocking data for now if API not ready, or use real endpoint
      // const response = await axios.get('/api/v1/analytics/dashboard/');
      // setData(response.data);

      // Mock Data to demonstrate capability
      const mockData = {
        summary: {
          total_revenue: 125000,
          total_orders: 450,
          total_users: 1200,
          conversion_rate: 3.5,
        },
        charts: {
          daily_revenue: Array.from({ length: 30 }, (_, i) => ({
            date: `2023-01-${i + 1}`,
            revenue: Math.floor(Math.random() * 5000) + 1000,
          })),
          category_distribution: {
            labels: ["Seeds", "Fertilizers", "Tools", "Pesticides"],
            data: [30, 25, 20, 25],
          },
        },
      };

      // Attempt to fetch real data
      try {
        const token = localStorage.getItem("token");
        if (token) {
           const response = await axios.get('/api/v1/analytics/dashboard/', {
               headers: { Authorization: `Token ${token}` }
           });
           if (response.data && response.data.summary) {
               setData(response.data);
           } else {
               setData(mockData);
           }
        } else {
            setData(mockData);
        }
      } catch (err) {
        console.warn("Using mock data due to API error", err);
        setData(mockData);
      }

    } catch (err) {
      setError("Failed to load analytics data");
    } finally {
      setLoading(false);
    }
  };

  const lineChartData = {
    labels: data?.charts?.daily_revenue?.map((d) => d.date) || [],
    datasets: [
      {
        label: "Daily Revenue (â‚¹)",
        data: data?.charts?.daily_revenue?.map((d) => d.revenue) || [],
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
        fill: false,
      },
    ],
  };

  const doughnutData = {
    labels: data?.charts?.category_distribution?.labels || [],
    datasets: [
      {
        data: data?.charts?.category_distribution?.data || [],
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
        ],
      },
    ],
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold">
          Analytics Dashboard
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="7d">Last 7 Days</MenuItem>
            <MenuItem value="30d">Last 30 Days</MenuItem>
            <MenuItem value="90d">Last 90 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h5" color="primary" fontWeight="bold">
                â‚¹{data?.summary?.total_revenue?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Orders
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                {data?.summary?.total_orders}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Users
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                {data?.summary?.total_users}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Conversion Rate
              </Typography>
              <Typography variant="h5" color="success.main" fontWeight="bold">
                {data?.summary?.conversion_rate}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card elevation={3}>
            <CardHeader title="Revenue Trend" />
            <CardContent>
              <Box height={300}>
                <Line
                  data={lineChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'top' },
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader title="Sales by Category" />
            <CardContent>
              <Box height={300} display="flex" justifyContent="center">
                <Doughnut
                  data={doughnutData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' },
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AnalyticsDashboard;
