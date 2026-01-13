import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  CircularProgress,
  Alert
} from '@mui/material';
import { Search, LocalShipping, Inventory, Factory, Store, CheckCircle } from '@mui/icons-material';

const SupplyChainTracker = () => {
  const [batchId, setBatchId] = useState('');
  const [batchData, setBatchData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!batchId) return;

    setLoading(true);
    setError(null);
    setBatchData(null);

    try {
      // Assuming public endpoint or handled via auth interceptor
      const response = await axios.get(`/api/v1/supply-chain/batch/${batchId}/`);
      setBatchData(response.data);
    } catch (err) {
      setError('Batch not found or access denied.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStepIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'production': return <Factory />;
      case 'transit': return <LocalShipping />;
      case 'warehouse': return <Inventory />;
      case 'retail': return <Store />;
      case 'sold': return <CheckCircle />;
      default: return <CheckCircle />;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, margin: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Traceability Tracker
      </Typography>

      <Paper component="form" onSubmit={handleSearch} sx={{ p: 2, display: 'flex', gap: 2, mb: 4 }}>
        <TextField
          fullWidth
          label="Enter Batch ID / Lot Number"
          variant="outlined"
          value={batchId}
          onChange={(e) => setBatchId(e.target.value)}
          placeholder="e.g., BATCH-2023-001"
        />
        <Button
          variant="contained"
          type="submit"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Search />}
        >
          Track
        </Button>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {batchData && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" gutterBottom>{batchData.product_name}</Typography>
            <Typography variant="body1" color="text.secondary">
              Batch ID: {batchData.batch_id} | Vendor: {batchData.vendor_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Current Status: <strong>{batchData.status.toUpperCase()}</strong>
            </Typography>
          </Box>

          <Typography variant="h6" gutterBottom>Journey History</Typography>
          <Stepper orientation="vertical">
            {batchData.journey_points.map((step, index) => (
              <Step key={step.id} active={true}>
                <StepLabel icon={getStepIcon(step.status)}>
                  <Typography variant="subtitle1">{step.status}</Typography>
                  <Typography variant="caption" display="block">
                    {new Date(step.timestamp).toLocaleString()}
                  </Typography>
                </StepLabel>
                <StepContent>
                  <Typography>{step.location}</Typography>
                  {step.handler && <Typography variant="body2">Handler: {step.handler}</Typography>}
                  {step.notes && <Typography variant="body2" color="text.secondary">{step.notes}</Typography>}
                </StepContent>
              </Step>
            ))}
            {/* Origin Point */}
            <Step active={true}>
                <StepLabel icon={<Factory />}>
                    <Typography variant="subtitle1">Origin</Typography>
                    <Typography variant="caption" display="block">
                        {new Date(batchData.created_at).toLocaleDateString()}
                    </Typography>
                </StepLabel>
                <StepContent>
                    <Typography>{batchData.origin_location}</Typography>
                    <Typography variant="body2">Manufactured by {batchData.vendor_name}</Typography>
                </StepContent>
            </Step>
          </Stepper>
        </Paper>
      )}
    </Box>
  );
};

export default SupplyChainTracker;
