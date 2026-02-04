import React, { useState, useEffect } from "react";
import {
  Container,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  Button,
  TextField,
  MenuItem,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  InputAdornment
} from "@mui/material";
import { Search, Agriculture } from "@mui/icons-material";
import { rentalsAPI } from "../services/api";
import { useAuth } from "../utils/AuthContext";

const RentalsPage = () => {
  const [equipment, setEquipment] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [openBooking, setOpenBooking] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    fetchEquipment();
  }, []);

  const fetchEquipment = async () => {
    try {
      const response = await rentalsAPI.getEquipment({ search: searchQuery });
      setEquipment(response.data);
    } catch (error) {
      console.error("Error fetching equipment:", error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchEquipment();
  };

  const handleBookClick = (item) => {
    if (!isAuthenticated) {
      window.location.href = "/login";
      return;
    }
    setSelectedEquipment(item);
    setOpenBooking(true);
  };

  const handleBookingSubmit = async () => {
    try {
      await rentalsAPI.bookEquipment({
        equipment_id: selectedEquipment.id,
        start_date: startDate,
        end_date: endDate,
      });
      alert("Booking successful!");
      setOpenBooking(false);
    } catch (error) {
      console.error("Booking error:", error);
      alert("Booking failed. Please try again.");
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h4" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Agriculture fontSize="large" color="primary" />
          Equipment Rentals
        </Typography>
        <form onSubmit={handleSearch}>
          <TextField
            size="small"
            placeholder="Search tractors, harvesters..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </form>
      </Box>

      <Grid container spacing={3}>
        {equipment.map((item) => (
          <Grid item key={item.id} xs={12} sm={6} md={4}>
            <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
              <CardMedia
                component="img"
                height="200"
                image={item.image || "https://via.placeholder.com/300?text=Equipment"}
                alt={item.name}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h6" component="div">
                  {item.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {item.description.substring(0, 100)}...
                </Typography>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    ₹{item.daily_rate}/day
                  </Typography>
                  <Chip
                    label={item.is_available ? "Available" : "Rented"}
                    color={item.is_available ? "success" : "default"}
                    size="small"
                  />
                </Box>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => handleBookClick(item)}
                  disabled={!item.is_available}
                >
                  Book Now
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openBooking} onClose={() => setOpenBooking(false)}>
        <DialogTitle>Book {selectedEquipment?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField
              label="Start Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <TextField
              label="End Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
            {startDate && endDate && (
              <Typography variant="subtitle1" align="right">
                Total: ₹
                {selectedEquipment?.daily_rate *
                  ((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24) + 1)}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenBooking(false)}>Cancel</Button>
          <Button onClick={handleBookingSubmit} variant="contained">Confirm Booking</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RentalsPage;
