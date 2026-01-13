import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import { Security, Warning, ErrorOutline, CheckCircle, Block } from '@mui/icons-material';

const SecurityDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Typically requires admin auth token
      const response = await axios.get('/api/v1/security/dashboard/');
      setData(response.data);
    } catch (err) {
      setError('Failed to load security data. Ensure you have admin permissions.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'success';
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return null;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Security fontSize="large" color="primary" /> Security Command Center
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Critical Threats</Typography>
              <Typography variant="h3" color="error">{data.summary.critical_alerts}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Unresolved Alerts</Typography>
              <Typography variant="h3" color="warning.main">{data.summary.unresolved_alerts}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Alerts</Typography>
              <Typography variant="h3">{data.summary.total_alerts}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>System Status</Typography>
              <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircle color="success" /> Protected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Alerts Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Recent Security Alerts</Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Severity</TableCell>
                <TableCell>Alert Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.recent_alerts.map((alert) => (
                <TableRow key={alert.id}>
                  <TableCell>
                    <Chip
                      label={alert.severity.toUpperCase()}
                      color={getSeverityColor(alert.severity)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{alert.title}</TableCell>
                  <TableCell>{alert.description}</TableCell>
                  <TableCell>{new Date(alert.created_at).toLocaleString()}</TableCell>
                  <TableCell>{alert.status}</TableCell>
                </TableRow>
              ))}
              {data.recent_alerts.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">No recent alerts</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default SecurityDashboard;
