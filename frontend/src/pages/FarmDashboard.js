import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box, Button, List, ListItem, ListItemText, Divider, Dialog, DialogTitle, DialogContent, TextField, DialogActions } from '@mui/material';
import { Add, Agriculture, WaterDrop, Grass } from '@mui/icons-material';
import { farmAPI } from '../services/api';

const FarmDashboard = () => {
  const [farms, setFarms] = useState([]); // Assuming single farm for simplicity but structure allows multiple
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [fields, setFields] = useState([]);
  const [openFieldDialog, setOpenFieldDialog] = useState(false);
  const [newField, setNewField] = useState({ name: '', size_acres: '', current_crop_id: '' });

  useEffect(() => {
    fetchFarmData();
  }, []);

  const fetchFarmData = async () => {
    try {
      const response = await farmAPI.getFarm();
      setFarms(response.data);
      if (response.data.length > 0) {
        setSelectedFarm(response.data[0]);
        // Ideally fetch fields here if not included in farm response
        // But our serializer includes them nested
        setFields(response.data[0].fields || []);
      }
    } catch (error) {
      console.error("Error fetching farm data:", error);
    }
  };

  const handleAddField = async () => {
    if (!selectedFarm) return;
    try {
      await farmAPI.createField(selectedFarm.id, newField);
      setOpenFieldDialog(false);
      fetchFarmData(); // Refresh
    } catch (error) {
      alert("Failed to add field");
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main', mb: 4 }}>
        My Farm Dashboard
      </Typography>

      {!selectedFarm ? (
        <Box textAlign="center" py={10}>
          <Typography variant="h5" color="text.secondary">You haven't set up your farm yet.</Typography>
          <Button
            variant="contained"
            size="large"
            sx={{ mt: 2 }}
            onClick={async () => {
                // Quick setup for demo
                try {
                    await farmAPI.createFarm({ name: "My Farm", location: "Default Location", size_acres: 10, soil_type: "Loam" });
                    fetchFarmData();
                } catch(e) { alert("Error creating farm"); }
            }}
          >
            Setup Farm
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* Farm Overview */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%', borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" color="primary">
                <Agriculture sx={{ mr: 1 }} /> Farm Details
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="subtitle1" gutterBottom><strong>Name:</strong> {selectedFarm.name}</Typography>
              <Typography variant="subtitle1" gutterBottom><strong>Location:</strong> {selectedFarm.location}</Typography>
              <Typography variant="subtitle1" gutterBottom><strong>Total Size:</strong> {selectedFarm.size_acres} Acres</Typography>
              <Typography variant="subtitle1"><strong>Soil Type:</strong> {selectedFarm.soil_type}</Typography>
            </Paper>
          </Grid>

          {/* Fields List */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, borderRadius: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" color="primary">Fields & Crops</Typography>
                <Button startIcon={<Add />} variant="outlined" onClick={() => setOpenFieldDialog(true)}>
                  Add Field
                </Button>
              </Box>
              <List>
                {fields.map((field) => (
                  <React.Fragment key={field.id}>
                    <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                      <ListItemText
                        primary={
                          <Typography variant="h6">
                            {field.name} ({field.size_acres} Acres)
                          </Typography>
                        }
                        secondary={
                          <Box mt={1}>
                            <Typography component="span" variant="body2" display="block" color="text.primary">
                              <strong>Current Crop:</strong> {field.current_crop_name || 'Fallow'}
                            </Typography>
                            {field.sowing_date && (
                                <Typography component="span" variant="body2" display="block">
                                <strong>Sowing Date:</strong> {field.sowing_date}
                                </Typography>
                            )}
                            <Box mt={1}>
                                <Button size="small" variant="outlined" startIcon={<WaterDrop />} sx={{ mr: 1 }}>Irrigate</Button>
                                <Button size="small" variant="outlined" startIcon={<Grass />}>Fertilize</Button>
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
                {fields.length === 0 && (
                    <Typography variant="body2" align="center" sx={{ py: 3, color: 'text.secondary' }}>No fields added yet.</Typography>
                )}
              </List>
            </Paper>
          </Grid>

          {/* Weather Widget Mock */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: '#e3f2fd', borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom color="primary.dark">Local Weather Forecast</Typography>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={4} textAlign="center">
                        <Typography variant="h3" color="primary.main">28°C</Typography>
                        <Typography variant="body1">Sunny</Typography>
                    </Grid>
                    <Grid item xs={6} sm={4} textAlign="center">
                        <Typography variant="h6" color="text.secondary">Humidity</Typography>
                        <Typography variant="h5">65%</Typography>
                    </Grid>
                    <Grid item xs={6} sm={4} textAlign="center">
                        <Typography variant="h6" color="text.secondary">Rain Chance</Typography>
                        <Typography variant="h5">10%</Typography>
                    </Grid>
                </Grid>
                <Typography variant="caption" display="block" textAlign="right" sx={{ mt: 1 }}>
                    Based on your location
                </Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      <Dialog open={openFieldDialog} onClose={() => setOpenFieldDialog(false)}>
        <DialogTitle>Add New Field</DialogTitle>
        <DialogContent>
            <TextField
                autoFocus
                margin="dense"
                label="Field Name"
                fullWidth
                variant="outlined"
                value={newField.name}
                onChange={(e) => setNewField({...newField, name: e.target.value})}
            />
            <TextField
                margin="dense"
                label="Size (Acres)"
                type="number"
                fullWidth
                variant="outlined"
                value={newField.size_acres}
                onChange={(e) => setNewField({...newField, size_acres: e.target.value})}
            />
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setOpenFieldDialog(false)}>Cancel</Button>
            <Button onClick={handleAddField} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FarmDashboard;
