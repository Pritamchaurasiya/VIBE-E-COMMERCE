import React, { useState, useEffect } from 'react';
import { predictiveAnalyticsAPI } from '../services/api';
import TopNav from '../components/layout/TopNav';
import BottomNav from '../components/layout/BottomNav';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Card, CardContent, Typography, Grid, Box, CircularProgress } from '@mui/material';
import { TrendingUp, Warning } from '@mui/icons-material';

const PredictiveDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await predictiveAnalyticsAPI.getPredictions();
      setData(response.data);
    } catch (error) {
      console.error("Failed to fetch predictions:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  // Transform churn risk for Pie Chart
  const churnRiskData = data?.churn_risk ? Object.keys(data.churn_risk).map(key => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: data.churn_risk[key]
  })) : [];

  const COLORS = ['#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="agri-theme">
      <TopNav />
      <main className="agri-main" style={{ padding: '20px' }}>
        <Typography variant="h4" gutterBottom style={{ color: '#2E7D32', fontWeight: 'bold' }}>
          Predictive Analytics Dashboard
        </Typography>

        <Grid container spacing={3}>
          {/* Sales Forecast */}
          <Grid item xs={12} md={8}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TrendingUp style={{ color: '#2E7D32', marginRight: 10 }} />
                  <Typography variant="h6">Sales Forecast (Next 7 Days)</Typography>
                </Box>
                <div style={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={data?.sales_forecast?.history}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="value" stroke="#8884d8" name="Historical Sales" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <Typography variant="body2" color="textSecondary" mt={2}>
                  * Dotted line represents predicted values (not yet implemented in chart visualization for this demo).
                  Next predicted value: ₹{data?.sales_forecast?.prediction?.predicted_value || 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Churn Risk */}
          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Warning style={{ color: '#FF9800', marginRight: 10 }} />
                  <Typography variant="h6">User Churn Risk</Typography>
                </Box>
                <div style={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={churnRiskData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey="value"
                        label
                      >
                        {churnRiskData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </main>
      <BottomNav />
    </div>
  );
};

export default PredictiveDashboard;
