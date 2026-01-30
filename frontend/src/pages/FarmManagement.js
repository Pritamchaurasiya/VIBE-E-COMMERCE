import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  CircularProgress,
  Alert,
} from "@mui/material";
import { Add, Landscape, Opacity, Terrain } from "@mui/icons-material";
import agriService from "../services/agriService";

const FarmManagement = () => {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState(null);
  const [newFarm, setNewFarm] = useState({
    name: "",
    location: "",
    size_acres: "",
    soil_type: "alluvial",
    irrigation_source: "rainfed",
  });

  const soilTypes = [
    { value: "alluvial", label: "Alluvial Soil" },
    { value: "black", label: "Black Soil" },
    { value: "red", label: "Red Soil" },
    { value: "laterite", label: "Laterite Soil" },
    { value: "arid", label: "Arid/Desert Soil" },
    { value: "forest", label: "Forest Soil" },
  ];

  const irrigationSources = [
    { value: "rainfed", label: "Rainfed" },
    { value: "canal", label: "Canal" },
    { value: "well", label: "Well/Tube Well" },
    { value: "drip", label: "Drip Irrigation" },
    { value: "sprinkler", label: "Sprinkler" },
  ];

  useEffect(() => {
    fetchFarms();
  }, []);

  const fetchFarms = async () => {
    try {
      const response = await agriService.getFarms();
      setFarms(response.data.results || response.data); // Handle pagination or list
      setLoading(false);
    } catch (err) {
      setError("Failed to load farms");
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await agriService.addFarm(newFarm);
      setOpen(false);
      fetchFarms();
      setNewFarm({
        name: "",
        location: "",
        size_acres: "",
        soil_type: "alluvial",
        irrigation_source: "rainfed",
      });
    } catch (err) {
      setError("Failed to create farm");
    }
  };

  if (loading) return <CircularProgress sx={{ display: "block", margin: "20px auto" }} />;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Farms
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpen(true)}
          sx={{ bgcolor: "#2e7d32", "&:hover": { bgcolor: "#1b5e20" } }}
        >
          Add Farm
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {farms.length === 0 ? (
        <Box textAlign="center" py={5} bgcolor="#f5f5f5" borderRadius={2}>
          <Landscape sx={{ fontSize: 60, color: "#bdbdbd" }} />
          <Typography variant="h6" color="textSecondary">
            No farms added yet. Add your first farm to get started!
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {farms.map((farm) => (
            <Grid item xs={12} md={6} lg={4} key={farm.id}>
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    {farm.name}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    {farm.location}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mt={2}>
                    <Landscape fontSize="small" color="action" />
                    <Typography variant="body2">
                      {farm.size_acres} Acres
                    </Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1} mt={1}>
                    <Terrain fontSize="small" color="action" />
                    <Typography variant="body2" textTransform="capitalize">
                      {farm.soil_type} Soil
                    </Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1} mt={1}>
                    <Opacity fontSize="small" color="action" />
                    <Typography variant="body2" textTransform="capitalize">
                      {farm.irrigation_source}
                    </Typography>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button size="small" color="primary">View Details</Button>
                  <Button size="small" color="error">Remove</Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Add Farm Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Add New Farm</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Farm Name"
              margin="normal"
              value={newFarm.name}
              onChange={(e) => setNewFarm({ ...newFarm, name: e.target.value })}
            />
            <TextField
              fullWidth
              label="Location"
              margin="normal"
              value={newFarm.location}
              onChange={(e) => setNewFarm({ ...newFarm, location: e.target.value })}
            />
            <TextField
              fullWidth
              label="Size (Acres)"
              type="number"
              margin="normal"
              value={newFarm.size_acres}
              onChange={(e) => setNewFarm({ ...newFarm, size_acres: e.target.value })}
            />
            <TextField
              select
              fullWidth
              label="Soil Type"
              margin="normal"
              value={newFarm.soil_type}
              onChange={(e) => setNewFarm({ ...newFarm, soil_type: e.target.value })}
            >
              {soilTypes.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              fullWidth
              label="Irrigation Source"
              margin="normal"
              value={newFarm.irrigation_source}
              onChange={(e) => setNewFarm({ ...newFarm, irrigation_source: e.target.value })}
            >
              {irrigationSources.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained" color="primary">
            Add Farm
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FarmManagement;
