import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Chip,
  CircularProgress,
  Alert,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import { AccessTime, WbSunny, AcUnit, Opacity } from '@mui/icons-material';
import axios from 'axios';

const CropCalendar = () => {
  const [calendarData, setCalendarData] = useState([]);
  const [currentMonth, setCurrentMonth] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(0);

  useEffect(() => {
    const fetchCalendar = async () => {
      try {
        const response = await axios.get('/api/v1/crop-calendar/');
        setCalendarData(response.data.calendar);
        setCurrentMonth(response.data.current_month);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching calendar:', err);
        setError('Failed to load crop calendar. Please try again later.');
        setLoading(false);
      }
    };

    fetchCalendar();
  }, []);

  const handleSeasonChange = (event, newValue) => {
    setSelectedSeason(newValue);
  };

  const getSeasonIcon = (seasonKey) => {
    switch (seasonKey) {
      case 'kharif': return <Opacity color="primary" />;
      case 'rabi': return <AcUnit color="info" />;
      case 'zaid': return <WbSunny color="warning" />;
      default: return <AccessTime />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold" color="primary">
        Smart Crop Calendar
      </Typography>
      <Typography variant="subtitle1" gutterBottom color="text.secondary">
        Plan your farming activities based on seasonal cycles. Current Month: <strong>{currentMonth}</strong>
      </Typography>

      <Paper sx={{ mt: 3, mb: 3 }}>
        <Tabs
          value={selectedSeason}
          onChange={handleSeasonChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
        >
          {calendarData.map((season, index) => (
            <Tab
              key={season.season_key}
              label={season.season_label}
              icon={getSeasonIcon(season.season_key)}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Paper>

      {calendarData.map((season, index) => (
        <div key={season.season_key} role="tabpanel" hidden={selectedSeason !== index}>
          {selectedSeason === index && (
            <Box>
              <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mr: 1, alignSelf: 'center' }}>
                  Best months:
                </Typography>
                {season.months.map(month => (
                  <Chip
                    key={month}
                    label={month}
                    size="small"
                    color={month === currentMonth ? "success" : "default"}
                    variant={month === currentMonth ? "filled" : "outlined"}
                  />
                ))}
              </Box>

              <Grid container spacing={3}>
                {season.crops.length > 0 ? (
                  season.crops.map((crop) => (
                    <Grid item key={crop.id} xs={12} sm={6} md={4}>
                      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 } }}>
                        {crop.image && (
                          <CardMedia
                            component="img"
                            height="140"
                            image={crop.image}
                            alt={crop.name}
                          />
                        )}
                        <CardContent sx={{ flexGrow: 1 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h6" component="h2">
                              {crop.name}
                            </Typography>
                            <Typography variant="h5">
                              {crop.icon}
                            </Typography>
                          </Box>
                          {crop.hindi_name && (
                            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                              ({crop.hindi_name})
                            </Typography>
                          )}
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            {crop.description ? crop.description.substring(0, 100) + '...' : 'No description available.'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))
                ) : (
                  <Grid item xs={12}>
                    <Alert severity="info">No specific crops listed for this season yet.</Alert>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </div>
      ))}
    </Container>
  );
};

export default CropCalendar;
