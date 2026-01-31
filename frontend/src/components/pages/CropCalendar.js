import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Grid, Card, CardContent, CardMedia,
  Chip, Tab, Tabs, useTheme, Paper
} from '@mui/material';
import {
  Agriculture, WbSunny, Opacity, AcUnit, CalendarMonth
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { cropsAPI } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSkeleton';

const CropCalendar = () => {
  const theme = useTheme();
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeason, setSelectedSeason] = useState('all');

  useEffect(() => {
    const fetchCrops = async () => {
      try {
        const response = await cropsAPI.getAll();
        // Assuming response.data.crops is the array
        setCrops(response.data.crops || []);
      } catch (error) {
        console.error("Failed to fetch crops", error);
      } finally {
        setLoading(false);
      }
    };
    fetchCrops();
  }, []);

  const seasons = [
    { value: 'all', label: 'All Seasons', icon: <CalendarMonth /> },
    { value: 'kharif', label: 'Kharif (Monsoon)', icon: <Opacity />, color: '#4caf50' },
    { value: 'rabi', label: 'Rabi (Winter)', icon: <AcUnit />, color: '#2196f3' },
    { value: 'zaid', label: 'Zaid (Summer)', icon: <WbSunny />, color: '#ff9800' },
  ];

  const filteredCrops = selectedSeason === 'all'
    ? crops
    : crops.filter(crop => crop.season === selectedSeason);

  const getSeasonColor = (season) => {
    const s = seasons.find(s => s.value === season);
    return s ? s.color : theme.palette.primary.main;
  };

  const getSeasonIcon = (season) => {
    const s = seasons.find(s => s.value === season);
    return s ? s.icon : <Agriculture />;
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LoadingSpinner />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold" color="primary">
          Smart Crop Calendar
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Plan your farming activities based on seasons
        </Typography>
      </Box>

      <Paper elevation={2} sx={{ mb: 4, borderRadius: 2 }}>
        <Tabs
          value={selectedSeason}
          onChange={(e, newValue) => setSelectedSeason(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
          indicatorColor="primary"
          textColor="primary"
          centered
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              fontSize: '1rem',
              fontWeight: 500,
            }
          }}
        >
          {seasons.map((season) => (
            <Tab
              key={season.value}
              value={season.value}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {season.icon}
                  {season.label}
                </Box>
              }
            />
          ))}
        </Tabs>
      </Paper>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Grid container spacing={3}>
          {filteredCrops.length > 0 ? (
            filteredCrops.map((crop) => (
              <Grid item xs={12} sm={6} md={4} key={crop.id}>
                <motion.div variants={itemVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      borderRadius: 3,
                      transition: 'transform 0.3s',
                      '&:hover': {
                        transform: 'translateY(-5px)',
                        boxShadow: 6
                      }
                    }}
                  >
                    <Box sx={{ position: 'relative' }}>
                      <CardMedia
                        component="img"
                        height="200"
                        image={crop.image || "https://via.placeholder.com/300x200?text=Crop+Image"}
                        alt={crop.name}
                      />
                      <Chip
                        label={crop.season.toUpperCase()}
                        size="small"
                        icon={getSeasonIcon(crop.season)}
                        sx={{
                          position: 'absolute',
                          top: 10,
                          right: 10,
                          bgcolor: 'white',
                          fontWeight: 'bold',
                          color: getSeasonColor(crop.season)
                        }}
                      />
                    </Box>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography gutterBottom variant="h5" component="div" fontWeight="bold">
                        {crop.name}
                      </Typography>
                      {crop.hindi_name && (
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          {crop.hindi_name}
                        </Typography>
                      )}
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {crop.description || "No description available."}
                      </Typography>

                      <Box sx={{ mt: 2 }}>
                        <Chip
                          label="Shop Products"
                          component="a"
                          href={`/crop/${crop.slug}`}
                          clickable
                          color="primary"
                          variant="outlined"
                          sx={{ width: '100%' }}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                  No crops found for this season.
                </Typography>
              </Box>
            </Grid>
          )}
        </Grid>
      </motion.div>
    </Container>
  );
};

export default CropCalendar;
