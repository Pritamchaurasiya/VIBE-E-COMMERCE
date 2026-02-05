import React, { useState, useEffect } from 'react';
import { Container, Typography, Card, CardContent, CardActions, Button, Grid, CircularProgress, Box, Chip } from '@mui/material';
import { schemesAPI } from '../services/api';

const SchemesPage = () => {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSchemes = async () => {
      try {
        const response = await schemesAPI.getSchemes();
        setSchemes(response.data);
      } catch (error) {
        console.error("Error fetching schemes:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSchemes();
  }, []);

  if (loading) return <Box display="flex" justifyContent="center" p={5}><CircularProgress /></Box>;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main', mb: 4 }}>
        Government Schemes
      </Typography>

      {schemes.length === 0 ? (
        <Typography variant="body1" align="center">No schemes found at the moment.</Typography>
      ) : (
        <Grid container spacing={3}>
            {schemes.map((scheme) => (
            <Grid item xs={12} key={scheme.id}>
                <Card sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, p: 2, boxShadow: 2 }}>
                <CardContent sx={{ flex: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                    <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
                        {scheme.name}
                    </Typography>
                    {scheme.is_active && <Chip label="Active" color="success" size="small" />}
                    </Box>
                    <Typography variant="body1" paragraph>
                    {scheme.description}
                    </Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" color="primary" gutterBottom>
                            Eligibility Criteria:
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                            {scheme.eligibility_criteria}
                            </Typography>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" color="primary" gutterBottom>
                            Benefits:
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                            {scheme.benefits}
                            </Typography>
                        </Grid>
                    </Grid>
                </CardContent>
                <CardActions sx={{ alignSelf: { xs: 'flex-start', md: 'center' }, p: 2 }}>
                    <Button
                    variant="contained"
                    href={scheme.application_link}
                    target="_blank"
                    disabled={!scheme.application_link}
                    size="large"
                    >
                    Apply Now
                    </Button>
                </CardActions>
                </Card>
            </Grid>
            ))}
        </Grid>
      )}
    </Container>
  );
};

export default SchemesPage;
