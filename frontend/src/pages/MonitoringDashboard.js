
import React from 'react';
import { Container, Grid, Paper, Typography } from '@mui/material';
import { SupplyChainTracker, SecurityDashboard, AnalyticsDashboard } from '../components/monitoring';

const MonitoringDashboard = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        System Monitoring Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <SupplyChainTracker />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <SecurityDashboard />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <AnalyticsDashboard />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default MonitoringDashboard;
