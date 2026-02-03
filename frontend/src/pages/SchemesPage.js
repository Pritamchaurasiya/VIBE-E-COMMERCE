import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Card, CardContent, Typography, Button,
  Chip, Box, TextField, MenuItem, Select, FormControl, InputLabel
} from '@mui/material';
import { schemesAPI } from '../services/api';
import { Description, Launch } from '@mui/icons-material';

const SchemesPage = () => {
  const [schemes, setSchemes] = useState([]);
  const [filterState, setFilterState] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSchemes();
  }, []);

  const fetchSchemes = async () => {
    try {
      const response = await schemesAPI.getAll();
      const data = response.data.results || response.data || [];
      setSchemes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching schemes:", error);
      setSchemes([]);
    }
  };

  const filteredSchemes = schemes.filter(scheme => {
    const matchesState = filterState === 'All' || scheme.state === filterState || scheme.state === 'All India';
    const matchesSearch = scheme.title.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesState && matchesSearch;
  });

  const states = ['All', 'All India', ...new Set(schemes.map(s => s.state).filter(s => s !== 'All India'))];

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#1976d2' }}>
        Government Schemes
      </Typography>
      <Typography variant="body1" paragraph>
        Explore agricultural schemes and subsidies available for you.
      </Typography>

      <Box sx={{ mb: 4, display: 'flex', gap: 2 }}>
        <TextField
          label="Search Schemes"
          variant="outlined"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FormControl fullWidth sx={{ minWidth: 200 }}>
          <InputLabel>State</InputLabel>
          <Select
            value={filterState}
            label="State"
            onChange={(e) => setFilterState(e.target.value)}
          >
            {states.map(state => (
              <MenuItem key={state} value={state}>{state}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {filteredSchemes.length > 0 ? (
          filteredSchemes.map((scheme) => (
            <Grid item key={scheme.id} xs={12}>
              <Card sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, p: 2 }}>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="div" color="primary">
                    {scheme.title}
                  </Typography>
                  <Chip label={scheme.state} size="small" color="secondary" sx={{ mt: 1, mb: 1 }} />
                  <Typography variant="body2" paragraph>
                    {scheme.description}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" fontWeight="bold">Eligibility:</Typography>
                      <Typography variant="body2">{scheme.eligibility}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" fontWeight="bold">Benefits:</Typography>
                      <Typography variant="body2">{scheme.benefits}</Typography>
                    </Grid>
                  </Grid>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
                  {scheme.link && (
                    <Button
                      variant="contained"
                      color="primary"
                      href={scheme.link}
                      target="_blank"
                      startIcon={<Launch />}
                    >
                      Apply / Details
                    </Button>
                  )}
                </Box>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Typography align="center">No schemes found matching your criteria.</Typography>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default SchemesPage;
