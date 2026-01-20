import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Cloud, CloudRain, Sun, CloudLightning, Wind, Droplets } from 'lucide-react';
import { Box, Typography, Card, CardContent, CircularProgress, Grid } from '@mui/material';

const WeatherWidget = () => {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                // In a real app, you might pass lat/long as query params
                const response = await axios.get('/api/v1/weather/');
                setWeather(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching weather:', err);
                setError('Failed to load weather data');
                setLoading(false);
            }
        };

        fetchWeather();
    }, []);

    const getWeatherIcon = (condition) => {
        switch (condition) {
            case 'Sunny':
                return <Sun size={32} color="#f9d71c" />;
            case 'Rainy':
                return <CloudRain size={32} color="#4a90e2" />;
            case 'Cloudy':
                return <Cloud size={32} color="#b0b0b0" />;
            case 'Partly Cloudy':
                return <Cloud size={32} color="#d4d4d4" />; // Or a custom sun+cloud icon if available
            case 'Stormy':
                return <CloudLightning size={32} color="#5e5e5e" />;
            default:
                return <Sun size={32} color="#f9d71c" />;
        }
    };

    if (loading) return <CircularProgress size={24} />;
    if (error) return null; // Hide on error to not disrupt UI

    if (!weather) return null;

    return (
        <Card sx={{
            background: 'linear-gradient(135deg, #e0f7fa 0%, #ffffff 100%)',
            borderRadius: 2,
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            mb: 3
        }}>
            <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Box>
                        <Typography variant="h6" color="textPrimary" fontWeight="bold">
                            {weather.location}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                        </Typography>
                    </Box>
                    <Box display="flex" alignItems="center">
                        {getWeatherIcon(weather.current.condition)}
                        <Typography variant="h4" ml={1} fontWeight="bold">
                            {weather.current.temp}°C
                        </Typography>
                    </Box>
                </Box>

                <Grid container spacing={2}>
                    <Grid item xs={6}>
                        <Box display="flex" alignItems="center" color="text.secondary">
                            <Droplets size={16} style={{ marginRight: 4 }} />
                            <Typography variant="body2">
                                Humidity: {weather.current.humidity}%
                            </Typography>
                        </Box>
                    </Grid>
                    <Grid item xs={6}>
                        <Box display="flex" alignItems="center" color="text.secondary">
                            <Wind size={16} style={{ marginRight: 4 }} />
                            <Typography variant="body2">
                                Wind: {weather.current.wind_speed} km/h
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>

                <Box mt={3} pt={2} borderTop="1px solid rgba(0,0,0,0.05)">
                    <Grid container justifyContent="space-between">
                        {weather.forecast.map((day, index) => (
                            <Grid item key={index} textAlign="center">
                                <Typography variant="caption" display="block" color="textSecondary">
                                    {day.day}
                                </Typography>
                                <Box my={0.5}>
                                    {getWeatherIcon(day.condition)}
                                </Box>
                                <Typography variant="caption" fontWeight="bold">
                                    {day.temp}°
                                </Typography>
                            </Grid>
                        ))}
                    </Grid>
                </Box>
            </CardContent>
        </Card>
    );
};

export default WeatherWidget;
