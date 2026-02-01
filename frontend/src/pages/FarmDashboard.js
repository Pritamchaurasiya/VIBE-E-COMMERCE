import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, TextField, Button, Grid, Paper, CircularProgress, Chip } from '@mui/material';
import { Agriculture, Save } from '@mui/icons-material';
import api from '../services/api';

const FarmDashboard = () => {
  const [farm, setFarm] = useState({
    farm_name: '',
    farm_size: 0,
    location: '',
    primary_crops: [],
    soil_type: '',
    irrigation_type: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newCrop, setNewCrop] = useState('');

  useEffect(() => {
    fetchFarmData();
  }, []);

  const fetchFarmData = async () => {
    try {
      const response = await api.get('/api/v1/my-farm/');
      setFarm(response.data);
    } catch (error) {
      console.error('Error fetching farm data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/api/v1/my-farm/', farm);
      alert('Farm details saved successfully!');
    } catch (error) {
      console.error('Error saving farm data:', error);
      alert('Failed to save farm details.');
    } finally {
      setSaving(false);
    }
  };

  const handleAddCrop = () => {
    if (newCrop.trim()) {
      setFarm(prev => ({
        ...prev,
        primary_crops: [...(prev.primary_crops || []), newCrop.trim()]
      }));
      setNewCrop('');
    }
  };

  const handleRemoveCrop = (cropToRemove) => {
    setFarm(prev => ({
      ...prev,
      primary_crops: prev.primary_crops.filter(crop => crop !== cropToRemove)
    }));
  };

  if (loading) return <Container sx={{ py: 4, textAlign: 'center' }}><CircularProgress /></Container>;

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Agriculture color="primary" /> My Farm Dashboard
      </Typography>
      <Paper sx={{ p: 4, mt: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Farm Name"
              value={farm.farm_name}
              onChange={(e) => setFarm({...farm, farm_name: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Size (Acres)"
              value={farm.farm_size}
              onChange={(e) => setFarm({...farm, farm_size: e.target.value})}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Location"
              value={farm.location}
              onChange={(e) => setFarm({...farm, location: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Soil Type"
              value={farm.soil_type}
              onChange={(e) => setFarm({...farm, soil_type: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Irrigation Type"
              value={farm.irrigation_type}
              onChange={(e) => setFarm({...farm, irrigation_type: e.target.value})}
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>Primary Crops</Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                size="small"
                label="Add Crop"
                value={newCrop}
                onChange={(e) => setNewCrop(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddCrop()}
              />
              <Button variant="outlined" onClick={handleAddCrop}>Add</Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {farm.primary_crops && farm.primary_crops.map((crop, index) => (
                <Chip key={index} label={crop} onDelete={() => handleRemoveCrop(crop)} />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              disabled={saving}
              size="large"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default FarmDashboard;
