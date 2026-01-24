import React, { useState, useEffect } from 'react';
import { Container, Typography, Card, CardContent, Grid, CircularProgress, TextField, Button, Box } from '@mui/material';
import { weatherAPI } from '../services/api';
import { WbSunny, Opacity, Air } from '@mui/icons-material';

const WeatherPage = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [city, setCity] = useState('Varanasi');

  const fetchWeather = async () => {
    setLoading(true);
    try {
      const response = await weatherAPI.getWeather(city);
      setWeather(response.data);
    } catch (error) {
      console.error("Error fetching weather", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather();
  }, []);

  if (loading) return <Container sx={{ py: 4, textAlign: 'center' }}><CircularProgress /></Container>;

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Agricultural Weather Forecast</Typography>
      <Box sx={{ mb: 4, display: 'flex', gap: 2 }}>
        <TextField
          label="City"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          size="small"
        />
        <Button variant="contained" onClick={fetchWeather}>Get Forecast</Button>
      </Box>

      {weather && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: 'primary.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h6">Current Weather</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
                  <WbSunny sx={{ fontSize: 60, mr: 2 }} />
                  <Box>
                    <Typography variant="h3">{weather.current.temp}°C</Typography>
                    <Typography variant="subtitle1">{weather.current.condition}</Typography>
                  </Box>
                </Box>
                <Grid container>
                  <Grid item xs={6} sx={{ display: 'flex', alignItems: 'center' }}>
                    <Opacity sx={{ mr: 1 }} /> {weather.current.humidity}% Humidity
                  </Grid>
                  <Grid item xs={6} sx={{ display: 'flex', alignItems: 'center' }}>
                    <Air sx={{ mr: 1 }} /> {weather.current.wind_speed} km/h Wind
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>5-Day Forecast</Typography>
            <Grid container spacing={2}>
              {weather.forecast.map((day, index) => (
                <Grid item xs={6} sm={2.4} key={index}>
                  <Card sx={{ height: '100%', textAlign: 'center' }}>
                    <CardContent>
                      <Typography variant="caption">{new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}</Typography>
                      <Typography variant="h6">{day.temp_high}° / {day.temp_low}°</Typography>
                      <Typography variant="body2" color="text.secondary">{day.condition}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default WeatherPage;
