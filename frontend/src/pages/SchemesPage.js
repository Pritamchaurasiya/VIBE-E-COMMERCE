import React, { useState, useEffect } from "react";
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  MenuItem,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip
} from "@mui/material";
import { ExpandMore, Policy } from "@mui/icons-material";
import { schemesAPI } from "../services/api";

const SchemesPage = () => {
  const [schemes, setSchemes] = useState([]);
  const [stateFilter, setStateFilter] = useState("");
  const [cropFilter, setCropFilter] = useState("");

  const states = ["All India", "Uttar Pradesh", "Maharashtra", "Punjab", "Haryana", "Madhya Pradesh"];

  useEffect(() => {
    fetchSchemes();
  }, [stateFilter, cropFilter]);

  const fetchSchemes = async () => {
    try {
      const response = await schemesAPI.getSchemes({
        state: stateFilter,
        crop: cropFilter
      });
      setSchemes(response.data);
    } catch (error) {
      console.error("Error fetching schemes:", error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <Policy fontSize="large" color="primary" />
          Government Schemes
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              select
              fullWidth
              label="Filter by State"
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
            >
              <MenuItem value="">All States</MenuItem>
              {states.map((state) => (
                <MenuItem key={state} value={state}>{state}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Filter by Crop"
              placeholder="e.g. Wheat, Rice"
              value={cropFilter}
              onChange={(e) => setCropFilter(e.target.value)}
            />
          </Grid>
        </Grid>
      </Box>

      <Box>
        {schemes.map((scheme) => (
          <Accordion key={scheme.id} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                <Typography variant="h6">{scheme.name}</Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Chip label={scheme.state || "Central"} size="small" color="primary" variant="outlined" />
                  {scheme.crops.map(crop => (
                    <Chip key={crop} label={crop} size="small" />
                  ))}
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Description</Typography>
              <Typography paragraph>{scheme.description}</Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" fontWeight="bold">Eligibility</Typography>
                  <Typography variant="body2" paragraph>{scheme.eligibility_criteria}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" fontWeight="bold">Benefits</Typography>
                  <Typography variant="body2" paragraph>{scheme.benefits}</Typography>
                </Grid>
              </Grid>

              {scheme.application_link && (
                <Button
                  variant="contained"
                  href={scheme.application_link}
                  target="_blank"
                  sx={{ mt: 2 }}
                >
                  Apply Now
                </Button>
              )}
            </AccordionDetails>
          </Accordion>
        ))}

        {schemes.length === 0 && (
          <Typography variant="h6" color="text.secondary" align="center" sx={{ mt: 4 }}>
            No schemes found matching your criteria.
          </Typography>
        )}
      </Box>
    </Container>
  );
};

export default SchemesPage;
