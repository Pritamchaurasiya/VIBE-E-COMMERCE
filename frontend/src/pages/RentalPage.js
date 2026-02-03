import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Card, CardMedia, CardContent, Typography, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Box, Chip
} from '@mui/material';
import { equipmentAPI, rentalsAPI } from '../services/api';
import { Agriculture, LocationOn } from '@mui/icons-material';

const RentalPage = () => {
  const [equipment, setEquipment] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [open, setOpen] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    fetchEquipment();
  }, []);

  const fetchEquipment = async () => {
    try {
      const response = await equipmentAPI.getAll();
      // Ensure we're setting an array, checking for DRF response format (results or direct array)
      const data = response.data.results || response.data || [];
      setEquipment(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching equipment:", error);
      setEquipment([]); // Fallback to empty array
    }
  };

  const handleBook = (item) => {
    setSelectedItem(item);
    setOpen(true);
  };

  const handleSubmit = async () => {
    try {
      await rentalsAPI.create({
        equipment_id: selectedItem.id,
        start_date: startDate,
        end_date: endDate
      });
      alert('Booking request sent successfully!');
      setOpen(false);
    } catch (error) {
      alert('Booking failed. Please try again.');
      console.error(error);
    }
  };

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
        Farm Equipment Rentals
      </Typography>
      <Typography variant="body1" paragraph>
        Rent high-quality farm machinery at affordable daily rates.
      </Typography>

      <Grid container spacing={3}>
        {equipment.length > 0 ? (
          equipment.map((item) => (
            <Grid item key={item.id} xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardMedia
                  component="img"
                  height="200"
                  image={item.image || "https://via.placeholder.com/300x200?text=Tractor"}
                  alt={item.name}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Typography gutterBottom variant="h5" component="div">
                      {item.name}
                    </Typography>
                    <Chip label={`₹${item.daily_rate}/day`} color="success" variant="outlined" />
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {item.description}
                  </Typography>
                  <Box display="flex" alignItems="center" mt={2}>
                    <LocationOn fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary" ml={0.5}>
                      {item.location}
                    </Typography>
                  </Box>
                  <Button
                    variant="contained"
                    fullWidth
                    sx={{ mt: 2, bgcolor: '#2e7d32', '&:hover': { bgcolor: '#1b5e20' } }}
                    startIcon={<Agriculture />}
                    onClick={() => handleBook(item)}
                  >
                    Book Now
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Typography variant="body1" color="text.secondary" align="center">
              No equipment available for rent at the moment.
            </Typography>
          </Grid>
        )}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Book {selectedItem?.name}</DialogTitle>
        <DialogContent>
          <TextField
            label="Start Date"
            type="date"
            fullWidth
            margin="normal"
            InputLabelProps={{ shrink: true }}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <TextField
            label="End Date"
            type="date"
            fullWidth
            margin="normal"
            InputLabelProps={{ shrink: true }}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="success">Confirm Booking</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RentalPage;
