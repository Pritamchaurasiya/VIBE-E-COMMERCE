import React, { useState, useEffect } from 'react';
import { Container, Typography, Card, CardContent, Grid, CircularProgress, List, ListItem, ListItemIcon, ListItemText, Divider, Alert, Box } from '@mui/material';
import { soilHealthAPI } from '../services/api';
import { Science, Agriculture, Grass } from '@mui/icons-material';

const SoilHealthPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await soilHealthAPI.getReport();
        setData(response.data.soil_health);
      } catch (error) {
        console.error("Error fetching soil health", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Container sx={{ py: 4, textAlign: 'center' }}><CircularProgress /></Container>;

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Soil Health Card</Typography>
      <Alert severity="info" sx={{ mb: 4 }}>Based on your latest soil sample analysis.</Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom><Science sx={{ verticalAlign: 'bottom', mr: 1 }} /> Nutrient Analysis</Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}><Typography variant="subtitle2">Nitrogen (N)</Typography></Grid>
                <Grid item xs={6}><Typography color="primary" fontWeight="bold">{data.nitrogen}</Typography></Grid>

                <Grid item xs={6}><Typography variant="subtitle2">Phosphorus (P)</Typography></Grid>
                <Grid item xs={6}><Typography color="primary" fontWeight="bold">{data.phosphorus}</Typography></Grid>

                <Grid item xs={6}><Typography variant="subtitle2">Potassium (K)</Typography></Grid>
                <Grid item xs={6}><Typography color="error" fontWeight="bold">{data.potassium}</Typography></Grid>

                <Grid item xs={12}><Divider sx={{ my: 1 }} /></Grid>

                <Grid item xs={6}><Typography variant="subtitle2">pH Level</Typography></Grid>
                <Grid item xs={6}><Typography fontWeight="bold">{data.ph_level}</Typography></Grid>

                <Grid item xs={6}><Typography variant="subtitle2">Organic Carbon</Typography></Grid>
                <Grid item xs={6}><Typography fontWeight="bold">{data.organic_carbon}</Typography></Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom><Agriculture sx={{ verticalAlign: 'bottom', mr: 1 }} /> Recommendations</Typography>
              <List dense>
                {data.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon><Grass color="success" /></ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Suitable Crops</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {data.suitable_crops.map((crop, index) => (
                  <Typography key={index} sx={{ bgcolor: 'secondary.light', color: 'secondary.contrastText', px: 2, py: 0.5, borderRadius: 4 }}>
                    {crop}
                  </Typography>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SoilHealthPage;
